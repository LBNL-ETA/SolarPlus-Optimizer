# RCEA tariff
from costcalculatorlib.cost_calculator.tariff_structure import TariffElemPeriod, TariffType, TouEnergyChargeTariff
from costcalculatorlib.cost_calculator.rate_structure import TouRateSchedule
from costcalculatorlib.cost_calculator.cost_calculator import CostCalculator
from costcalculatorlib.openei_tariff.openei_tariff_analyzer import *


class SolarPlusCombinedCostCalculator:
    """
    This class combines the various bills for the Solar+ fieldtest:
        - PG&E E19s charges
        - PG&E E19S generation credit
        - RCEA generation charges linked to E19s
    """

    def __init__(self):

        # Read the JSON / OpenEI api containing the tariffs
        self.openei_pge_charges = OpenEI_tariff(utility_id='14328', sector='Commercial', tariff_rate_of_interest='E-19',
                                                distrib_level_of_interest='Secondary', phasewing=None, tou=True,
                                                pdp=False, option_exclusion=['Option R', 'Voluntary'])
        self.openei_pge_generation_credits = OpenEI_tariff(utility_id='14328', sector='Commercial',
                                                           tariff_rate_of_interest='E-19_GENERATIONCREDIT',
                                                           distrib_level_of_interest='Secondary', phasewing=None,
                                                           tou=True, pdp=False,
                                                           option_exclusion=['Option R', 'Voluntary'])
        self.openei_rcea_charges = OpenEI_tariff(utility_id='rcea', sector='Commercial',
                                                 tariff_rate_of_interest='E-19S', distrib_level_of_interest='Secondary',
                                                 phasewing=None, tou=True, pdp=False)

        read_from_file_success = True
        for tariff_openei in [self.openei_pge_charges, self.openei_pge_generation_credits, self.openei_rcea_charges]:
            if tariff_openei.read_from_json() != 0:  # Reading revised JSON blocks containing the utility rates
                print "An error occurred when reading the JSON file ! Abording"
                read_from_file_success = False
                break

        # Create the cost calculator objects
        if read_from_file_success:

            # PG&E charges for E19S complete
            self.pge_charges_costcalculator = CostCalculator()
            tariff_struct_from_openei_data(self.openei_pge_charges, self.pge_charges_costcalculator)

            # PG&E credits for E19S generation and PCIA+fees
            self.pge_generation_credit_costcalculator = CostCalculator()
            tariff_struct_from_openei_data(self.openei_pge_generation_credits,
                                           self.pge_generation_credit_costcalculator)
            for b_tariff in self.get_pcia_and_fees():
                self.pge_generation_credit_costcalculator.add_tariff(b_tariff,
                                                                     str(TariffType.ENERGY_CUSTOM_CHARGE.value))

            # RCEA generation charges linked to E19S
            self.rcea_charges_costcalculator = CostCalculator()
            tariff_struct_from_openei_data(self.openei_rcea_charges, self.rcea_charges_costcalculator)

    def compute_bill(self, df):
        """
        Get the bill (pg&e and rcea, in $, for the energy consumption in df) as a tuple of float
        """

        costcalc_object_l = [self.pge_charges_costcalculator, self.pge_generation_credit_costcalculator,
                             self.rcea_charges_costcalculator]
        bill_l = {'pge_charge': 0, 'pge_generation_credit': 0, 'rcea_charges': 0}

        for bill_key, costcalc_object in zip(bill_l.keys(), costcalc_object_l):  # compute bill for each component
            bill = costcalc_object.compute_bill(df)
            t, tt, ttt = costcalc_object.print_aggregated_bill(bill, False)
            bill_l[bill_key] += t

        pge_bill = bill_l['pge_charge'] + bill_l['pge_generation_credit']
        rcea_bill = bill_l['rcea_charges']
        print rcea_bill
        return pge_bill, rcea_bill

    def get_elec_price(self, range_date, timestep=TariffElemPeriod.QUARTERLY):
        """
        Get the price of electricity as a pandas dataframe, separated per type of tariff.
        """

        # Get the PG&E main elec components
        prices_total, map_type = self.pge_charges_costcalculator.get_electricity_price(range_date, timestep)
        prices_total = prices_total.fillna(0)

        # Remove the generation charges
        prices_pge_gen, map_type = self.pge_generation_credit_costcalculator.get_electricity_price(range_date, timestep)
        prices_total = prices_total.add(prices_pge_gen.fillna(0))

        # Add the RCEA generation charges
        prices_rcea, map_type = self.rcea_charges_costcalculator.get_electricity_price(range_date, timestep)
        prices_total = prices_total.add(prices_rcea.fillna(0))

        return prices_total

    def get_pcia_and_fees(self):
        """
        Create the Rate structure for modelling the Power Charge Indifference Adjustment Rates and the Franchise Fees
        """

        map_date_to_pcia = [("07/01/2017", "06/30/2018", 0.02), ("07/01/2018", "06/30/2019", 0.02)]
        map_date_to_fees = [("07/01/2017", "06/30/2018", 0.00062), ("07/01/2018", "06/30/2019", 0.00062)]
        blocks = []
        for i in range(len(map_date_to_pcia)):
            pcia_start_date, pcia_end_date, pcia_rate = map_date_to_pcia[i]
            fee_start_date, fee_end_date, fee_rate = map_date_to_fees[i]

            rate_struct = {}
            rate_struct['allmonth'] = {TouRateSchedule.MONTHLIST_KEY: range(1, 13), TouRateSchedule.DAILY_RATE_KEY:
                {
                    'allweek':
                        {
                            TouRateSchedule.DAYSLIST_KEY: range(7),
                            TouRateSchedule.RATES_KEY: pcia_rate + fee_rate
                        }
                }
                                       }
            tariff_rate = TouRateSchedule(rate_struct)
            start = datetime.strptime(pcia_start_date, '%m/%d/%Y').replace(tzinfo=pytz.timezone('UTC'))
            end = datetime.strptime(pcia_end_date, '%m/%d/%Y').replace(tzinfo=pytz.timezone('UTC'))

            blocks.append(TouEnergyChargeTariff((start, end), tariff_rate))

        return blocks

