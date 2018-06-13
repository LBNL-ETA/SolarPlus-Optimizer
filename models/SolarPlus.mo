within ;
package SolarPlus "This package contains models for MPC control optimization."

  package Envelope "Package for envelope thermal response models"
    model R1C1 "Zone thermal model"
      parameter Modelica.SIunits.HeatCapacity C=1e6 "Heat capacity of zone";
      parameter Modelica.SIunits.ThermalResistance R=0.01 "Thermal resistance of zone";
      parameter Modelica.SIunits.Temperature Tzone_0(fixed=true) "Initial temperature of zone";
      Modelica.Thermal.HeatTransfer.Components.HeatCapacitor capAir(C=C, T(fixed=true,
                                                                         start = Tzone_0))
        annotation (Placement(transformation(extent={{-10,0},{10,20}})));
    Modelica.Thermal.HeatTransfer.Components.ThermalResistor resAdj(R=R)
        annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
      Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow preHeat
        annotation (Placement(transformation(extent={{-58,-50},{-38,-30}})));
      Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow preCool
        annotation (Placement(transformation(extent={{-58,-70},{-38,-50}})));
      Modelica.Blocks.Interfaces.RealInput qHeat "Heat floww for heating"
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.Blocks.Interfaces.RealInput qCool "Heat flow for cooling"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
      Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port_adj
        annotation (Placement(transformation(extent={{-110,50},{-90,70}})));
      Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port_cap
        annotation (Placement(transformation(extent={{-8,-10},{12,10}})));
    equation
      connect(resAdj.port_b, capAir.port)
        annotation (Line(points={{-20,0},{0,0}}, color={191,0,0}));
      connect(preHeat.port, capAir.port)
        annotation (Line(points={{-38,-40},{0,-40},{0,0}}, color={191,0,0}));
      connect(preCool.port, capAir.port)
        annotation (Line(points={{-38,-60},{0,-60},{0,0}}, color={191,0,0}));
      connect(qHeat, preHeat.Q_flow)
        annotation (Line(points={{-120,-40},{-58,-40}}, color={0,0,127}));
      connect(qCool, preCool.Q_flow) annotation (Line(points={{-120,-80},{-80,-80},{
              -80,-60},{-58,-60}}, color={0,0,127}));
      connect(resAdj.port_a, port_adj) annotation (Line(points={{-40,0},{-70,0},{-70,
              60},{-100,60}}, color={191,0,0}));
      connect(capAir.port, port_cap)
        annotation (Line(points={{0,0},{2,0}}, color={191,0,0}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
          Rectangle(
            extent={{-100,100},{100,-100}},
            lineColor={0,0,0},
            fillColor={255,231,231},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-64,66},{-22,52}},
            lineColor={0,0,0},
            fillColor={255,231,231},
            fillPattern=FillPattern.Solid),
          Line(points={{-64,60},{-100,60}},
                                          color={0,0,0}),
          Line(points={{2,60},{-22,60}},
                                       color={0,0,0}),
          Line(points={{2,60},{2,-14}},color={0,0,0}),
          Line(points={{14,-14},{-10,-14}}, color={0,0,0}),
          Line(points={{14,-22},{-10,-22}}, color={0,0,0}),
          Line(points={{14,-36},{-10,-36}}, color={0,0,0}),
          Line(points={{2,-22},{2,-36}}, color={0,0,0}),
          Line(points={{12,-40},{-8,-40}}, color={0,0,0}),
          Line(points={{10,-44},{-6,-44}}, color={0,0,0}),
          Line(points={{-46,-40},{-100,-40}},
                                       color={0,0,0}),
          Line(points={{-46,-80},{-100,-80}},
                                       color={0,0,0}),
          Line(points={{-46,0},{-46,-80}},
                                       color={0,0,0}),
          Line(points={{2,0},{-46,0}}, color={0,0,0}),
            Ellipse(extent={{-88,-28},{-62,-54}}, lineColor={238,46,47}),
            Line(points={{-62,-40},{-70,-34}}, color={238,46,47}),
            Line(points={{-62,-40},{-70,-46}}, color={238,46,47}),
            Ellipse(extent={{-88,-68},{-62,-94}}, lineColor={28,108,200}),
            Line(points={{-62,-80},{-70,-74}}, color={28,108,200}),
            Line(points={{-62,-80},{-70,-86}}, color={28,108,200}),
            Text(
              extent={{-150,140},{150,100}},
              textString="%name",
              lineColor={0,0,255})}),
                                Diagram(coordinateSystem(preserveAspectRatio=
              false)));
    end R1C1;

    package Training
      extends Modelica.Icons.ExamplesPackage;
      model R1C1
      import MPC = SolarPlus;
        extends Modelica.Icons.Example;
      MPC.Envelope.R1C1 r1C1_1
        annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealOutput Tzone "Zone air temperature"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Interfaces.RealInput qHeat "Heat floww for heating"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealInput qCool "Heat flow for cooling"
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.Blocks.Interfaces.RealInput Tadj "Adjacent temperature"
        annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
      Buildings.HeatTransfer.Sources.PrescribedTemperature preTadj
        annotation (Placement(transformation(extent={{-60,50},{-40,70}})));
      Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTzone
        annotation (Placement(transformation(extent={{40,-10},{60,10}})));
      equation
      connect(r1C1_1.qHeat, qHeat) annotation (Line(points={{-12,-4},{-40,-4},{
              -40,0},{-120,0}}, color={0,0,127}));
      connect(r1C1_1.qCool, qCool) annotation (Line(points={{-12,-8},{-40,-8},{
              -40,-40},{-120,-40}}, color={0,0,127}));
      connect(Tadj, preTadj.T)
        annotation (Line(points={{-120,60},{-62,60}}, color={0,0,127}));
      connect(preTadj.port, r1C1_1.port_adj) annotation (Line(points={{-40,60},
              {-20,60},{-20,6},{-10,6}}, color={191,0,0}));
      connect(senTzone.T, Tzone)
        annotation (Line(points={{60,0},{110,0}}, color={0,0,127}));
      connect(senTzone.port, r1C1_1.port_cap)
        annotation (Line(points={{40,0},{0.2,0}}, color={191,0,0}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end R1C1;
    end Training;
  end Envelope;

  package HVACR
    model SimpleHeaterCooler
      "A simple heater and cooler with constant efficiency and COP"
      parameter Modelica.SIunits.Power heatingCap = 10000 "Capacity of heater";
      parameter Modelica.SIunits.DimensionlessRatio heatingEff = 0.99 "Efficiency of heater";
      parameter Modelica.SIunits.Power coolingCap = 10000 "Capacity of cooler";
      parameter Modelica.SIunits.DimensionlessRatio coolingCOP = 3 "COP of cooler";
      Modelica.Blocks.Math.Gain heatingCapGain(k=heatingCap)
        annotation (Placement(transformation(extent={{-20,70},{0,90}})));
      Modelica.Blocks.Math.Gain coolingCapGain(k=coolingCap)
        annotation (Placement(transformation(extent={{-20,-90},{0,-70}})));
      Modelica.Blocks.Math.Gain heatingPowerGain(k=1/heatingEff)
        annotation (Placement(transformation(extent={{60,10},{80,30}})));
      Modelica.Blocks.Math.Gain coolingPowerGain(k=1/coolingCOP)
        annotation (Placement(transformation(extent={{60,-90},{80,-70}})));
      Modelica.Blocks.Interfaces.RealOutput PCool(unit="W")
      "Cooling electrical power output"
        annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
      Modelica.Blocks.Interfaces.RealOutput PHeat(unit="W")
      "Heating electrical power output"
        annotation (Placement(transformation(extent={{100,10},{120,30}}),
            iconTransformation(extent={{100,10},{120,30}})));
      Modelica.Blocks.Interfaces.RealInput uHeat "Heating signal input"
        annotation (Placement(transformation(extent={{-140,60},{-100,100}})));
      Modelica.Blocks.Interfaces.RealInput uCool "Cooling signal input"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}}),
            iconTransformation(extent={{-140,-100},{-100,-60}})));
      Modelica.Blocks.Interfaces.RealOutput qHeat(unit="W") "Heating heatflow output"
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      Modelica.Blocks.Interfaces.RealOutput qCool(unit="W") "Cooling heatflow output"
        annotation (Placement(transformation(extent={{100,-50},{120,-30}}),
            iconTransformation(extent={{100,-50},{120,-30}})));
      Modelica.Blocks.Math.Gain negHeatFlow(k=-1)
        annotation (Placement(transformation(extent={{60,-50},{80,-30}})));
    equation
      connect(heatingCapGain.y, heatingPowerGain.u) annotation (Line(points={{1,80},{
              20,80},{20,20},{58,20}},                color={0,0,127}));
      connect(coolingCapGain.y, coolingPowerGain.u) annotation (Line(points={{1,-80},
              {58,-80}},                 color={0,0,127}));
      connect(coolingPowerGain.y, PCool)
        annotation (Line(points={{81,-80},{110,-80}}, color={0,0,127}));
      connect(heatingPowerGain.y, PHeat)
        annotation (Line(points={{81,20},{110,20}}, color={0,0,127}));
      connect(heatingCapGain.u, uHeat) annotation (Line(points={{-22,80},{-120,80}},
                              color={0,0,127}));
      connect(uCool, coolingCapGain.u) annotation (Line(points={{-120,-80},{-22,-80}},
                                   color={0,0,127}));
      connect(heatingCapGain.y, qHeat) annotation (Line(points={{1,80},{60,80},{60,60},
              {110,60}},         color={0,0,127}));
      connect(coolingPowerGain.u, negHeatFlow.u) annotation (Line(points={{58,
              -80},{20,-80},{20,-40},{58,-40}}, color={0,0,127}));
      connect(negHeatFlow.y, qCool)
        annotation (Line(points={{81,-40},{110,-40}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-100,100},{100,0}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-100,0},{100,-100}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-150,140},{150,100}},
              textString="%name",
              lineColor={0,0,255})}),                                Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end SimpleHeaterCooler;

    package Controllers
      model SingleStageCoolingController
        parameter Real deadband = 1 "Deadband of controller";
        Modelica.Blocks.Interfaces.RealInput Tset "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealInput Tmeas "Temperature measured"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
        Modelica.Blocks.Logical.OnOffController onOffController(bandwidth=deadband)
          annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
        Modelica.Blocks.Math.BooleanToReal booleanToReal
          annotation (Placement(transformation(extent={{42,-10},{62,10}})));
        Modelica.Blocks.Interfaces.RealOutput y "Controller output"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
        Modelica.Blocks.MathBoolean.Not not1
          annotation (Placement(transformation(extent={{22,-4},{30,4}})));
      equation
        connect(Tmeas, onOffController.u) annotation (Line(points={{-120,-40},{-60,-40},
                {-60,-6},{-12,-6}}, color={0,0,127}));
        connect(Tset, onOffController.reference) annotation (Line(points={{-120,60},{-60,
                60},{-60,6},{-12,6}}, color={0,0,127}));
        connect(booleanToReal.y, y)
          annotation (Line(points={{63,0},{110,0}}, color={0,0,127}));
        connect(booleanToReal.u, not1.y)
          annotation (Line(points={{40,0},{30.8,0}}, color={255,0,255}));
        connect(not1.u, onOffController.y)
          annotation (Line(points={{20.4,0},{11,0}}, color={255,0,255}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Line(points={{-100,60},{100,60}}, color={0,0,0}),
              Line(
                points={{-100,90},{100,90}},
                color={0,0,0},
                pattern=LinePattern.Dot),
              Line(
                points={{-100,30},{100,30}},
                color={0,0,0},
                pattern=LinePattern.Dot),
              Line(points={{-100,80},{-68,90},{-22,30},{28,90},{74,30}}, color={28,108,
                    200}),
              Line(points={{-100,-72},{100,-72}}, color={0,0,0}),
              Rectangle(
                extent={{-66,0},{-20,-72}},
                lineColor={28,108,200},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Rectangle(
                extent={{28,0},{74,-72}},
                lineColor={28,108,200},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Text(
                extent={{-150,140},{150,100}},
                textString="%name",
                lineColor={0,0,255})}),                                Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end SingleStageCoolingController;

      model TwoStageCoolingController
        parameter Real deadband = 1 "Deadband of controller";
        Modelica.Blocks.Interfaces.RealInput Tset "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealInput Tmeas "Temperature measured"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
        Modelica.Blocks.Logical.OnOffController stage1(bandwidth=deadband)
          annotation (Placement(transformation(extent={{-80,20},{-60,40}})));
        Modelica.Blocks.Math.BooleanToReal booleanToReal1
          annotation (Placement(transformation(extent={{-40,20},{-20,40}})));
        Modelica.Blocks.Interfaces.RealOutput y "Controller output"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
        Modelica.Blocks.MathBoolean.Not not1
          annotation (Placement(transformation(extent={{-54,26},{-46,34}})));
        Modelica.Blocks.Math.Gain stage1div(k=0.5)
          annotation (Placement(transformation(extent={{-12,20},{8,40}})));
        Modelica.Blocks.Logical.OnOffController stage2(bandwidth=deadband)
          annotation (Placement(transformation(extent={{-30,-40},{-10,-20}})));
        Modelica.Blocks.Sources.Constant const(k=deadband)
          annotation (Placement(transformation(extent={{-90,-20},{-70,0}})));
        Modelica.Blocks.Math.Add add
          annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
        Modelica.Blocks.MathBoolean.Not not2
          annotation (Placement(transformation(extent={{-4,-34},{4,-26}})));
        Modelica.Blocks.Math.BooleanToReal booleanToReal2
          annotation (Placement(transformation(extent={{10,-40},{30,-20}})));
        Modelica.Blocks.Math.Add add1
          annotation (Placement(transformation(extent={{74,-10},{94,10}})));
        Modelica.Blocks.Math.Gain stage2div(k=0.5)
          annotation (Placement(transformation(extent={{38,-40},{58,-20}})));
      equation
        connect(booleanToReal1.u, not1.y)
          annotation (Line(points={{-42,30},{-45.2,30}}, color={255,0,255}));
        connect(not1.u, stage1.y)
          annotation (Line(points={{-55.6,30},{-59,30}}, color={255,0,255}));
        connect(Tset, stage1.reference) annotation (Line(points={{-120,60},{-90,60},{-90,
                36},{-82,36}}, color={0,0,127}));
        connect(Tmeas, stage1.u) annotation (Line(points={{-120,-40},{-96,-40},{-96,24},
                {-82,24}}, color={0,0,127}));
        connect(booleanToReal1.y, stage1div.u)
          annotation (Line(points={{-19,30},{-14,30}}, color={0,0,127}));
        connect(const.y, add.u2) annotation (Line(points={{-69,-10},{-66,-10},{-66,-6},
                {-62,-6}}, color={0,0,127}));
        connect(Tset, add.u1) annotation (Line(points={{-120,60},{-90,60},{-90,6},{-62,
                6}}, color={0,0,127}));
        connect(Tmeas, stage2.u) annotation (Line(points={{-120,-40},{-40,-40},{-40,-36},
                {-32,-36}}, color={0,0,127}));
        connect(add.y, stage2.reference) annotation (Line(points={{-39,0},{-36,0},{-36,
                -24},{-32,-24}}, color={0,0,127}));
        connect(stage2.y, not2.u)
          annotation (Line(points={{-9,-30},{-5.6,-30}}, color={255,0,255}));
        connect(not2.y, booleanToReal2.u)
          annotation (Line(points={{4.8,-30},{8,-30}}, color={255,0,255}));
        connect(booleanToReal2.y, stage2div.u)
          annotation (Line(points={{31,-30},{36,-30}}, color={0,0,127}));
        connect(stage2div.y, add1.u2) annotation (Line(points={{59,-30},{66,-30},{66,-6},
                {72,-6}}, color={0,0,127}));
        connect(stage1div.y, add1.u1)
          annotation (Line(points={{9,30},{66,30},{66,6},{72,6}}, color={0,0,127}));
        connect(add1.y, y)
          annotation (Line(points={{95,0},{110,0}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Line(points={{-100,60},{100,60}}, color={0,0,0}),
              Line(
                points={{-100,90},{100,90}},
                color={0,0,0},
                pattern=LinePattern.Dot),
              Line(
                points={{-100,30},{100,30}},
                color={0,0,0},
                pattern=LinePattern.Dot),
              Line(points={{-100,80},{-70,90},{-38,90},{28,90},{74,30}}, color={28,108,
                    200}),
              Line(points={{-100,-72},{100,-72}}, color={0,0,0}),
              Rectangle(
                extent={{-66,0},{28,-72}},
                lineColor={28,108,200},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Rectangle(
                extent={{28,-40},{74,-72}},
                lineColor={28,108,200},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Text(
                extent={{-150,140},{150,100}},
                textString="%name",
                lineColor={0,0,255})}),                                Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end TwoStageCoolingController;

      model SingleStageHeatingController
        parameter Real deadband = 1 "Deadband of controller";
        Modelica.Blocks.Interfaces.RealInput Tset "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealInput Tmeas "Temperature measured"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
        Modelica.Blocks.Logical.OnOffController onOffController(bandwidth=deadband)
          annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
        Modelica.Blocks.Math.BooleanToReal booleanToReal
          annotation (Placement(transformation(extent={{42,-10},{62,10}})));
        Modelica.Blocks.Interfaces.RealOutput y "Controller output"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      equation
        connect(Tmeas, onOffController.u) annotation (Line(points={{-120,-40},{-60,-40},
                {-60,-6},{-12,-6}}, color={0,0,127}));
        connect(Tset, onOffController.reference) annotation (Line(points={{-120,60},{-60,
                60},{-60,6},{-12,6}}, color={0,0,127}));
        connect(booleanToReal.y, y)
          annotation (Line(points={{63,0},{110,0}}, color={0,0,127}));
        connect(onOffController.y, booleanToReal.u)
          annotation (Line(points={{11,0},{40,0}}, color={255,0,255}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Line(points={{-100,60},{100,60}}, color={0,0,0}),
              Line(
                points={{-100,90},{100,90}},
                color={0,0,0},
                pattern=LinePattern.Dot),
              Line(
                points={{-100,30},{100,30}},
                color={0,0,0},
                pattern=LinePattern.Dot),
              Line(points={{-100,80},{-68,90},{-22,30},{28,90},{74,30}}, color={238,
                    46,47}),
              Line(points={{-100,-72},{100,-72}}, color={0,0,0}),
              Rectangle(
                extent={{-20,0},{30,-72}},
                lineColor={238,46,47},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Text(
                extent={{-150,140},{150,100}},
                textString="%name",
                lineColor={0,0,255})}),                                Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end SingleStageHeatingController;
    end Controllers;
  end HVACR;

  package Batteries "Package for battery models"

    model Simple
      "Simple battery model with SOC as state including charging, discharging"
      parameter Modelica.SIunits.Energy Ecap  "Battery capacity";
      parameter Modelica.SIunits.Power P_cap_charge "Charging capacity";
      parameter Modelica.SIunits.Power P_cap_discharge "Discharging capacity";
      parameter Modelica.SIunits.DimensionlessRatio eta_charge=0.9 "Charging efficiency";
      parameter Modelica.SIunits.DimensionlessRatio eta_discharge=0.9 "Discharging efficiency";
      parameter Modelica.SIunits.DimensionlessRatio SOC_0 "Initial state of charge";
      Modelica.SIunits.Energy E(fixed=true,start=SOC_0*Ecap) "Battery energy level";
      Modelica.SIunits.Power P_loss_charge "Charging losses of battery";
      Modelica.SIunits.Power P_loss_discharge "Discharging losses of battery";
      Modelica.Blocks.Interfaces.RealInput uCharge(min=0, max=1)
        "Control signal for charging"
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.Blocks.Interfaces.RealInput uDischarge(min=0, max=1)
        "Control signal for discharging"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,-12},{124,12}})));
      Modelica.Blocks.Interfaces.RealOutput Pcharge(unit="W") "Battery charging power"
        annotation (Placement(transformation(extent={{100,-52},{124,-28}})));
      Modelica.Blocks.Interfaces.RealOutput Pdischarge(unit="W") "Battery discharging power"
        annotation (Placement(transformation(extent={{100,-92},{124,-68}})));
    equation
      SOC = E/Ecap;
      der(E) =Pcharge - Pdischarge - P_loss_charge - P_loss_discharge;
      Pcharge = uCharge*P_cap_charge;
      Pdischarge = uDischarge*P_cap_discharge;
      P_loss_charge =Pcharge*(1 - eta_charge);
      P_loss_discharge =Pdischarge*(1 - eta_discharge);
      annotation (Icon(graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-60,20},{62,-56}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-40,42},{-18,20}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{20,42},{42,20}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-250,170},{250,110}},
              textString="%name",
              lineColor={0,0,255})}));
    end Simple;

    package Controllers
      model Controller
        // Controller
        parameter Modelica.SIunits.Time peakStart = 8*3600 "Daily start time of peak period" annotation(Dialog(group="Controller"));
        parameter Modelica.SIunits.Time peakEnd = 16*3600 "Daily end time of peak period" annotation(Dialog(group="Controller"));
        parameter Modelica.SIunits.Power interchangeLimit "Limit of interchange power (+ for import limit, - for export limit)" annotation(Dialog(group="Controller"));
        // Battery Characteristics
        parameter Modelica.SIunits.Energy Ecap  "Battery capacity" annotation(Dialog(group="Battery Characteristics"));
        parameter Modelica.SIunits.Power P_cap_charge "Charging capacity" annotation(Dialog(group="Battery Characteristics"));
        parameter Modelica.SIunits.Power P_cap_discharge "Discharging capacity" annotation(Dialog(group="Battery Characteristics"));
        Modelica.Blocks.Interfaces.RealInput clockTime "Clock time"
          annotation (Placement(transformation(extent={{-140,60},{-100,100}})));
        Modelica.Blocks.Interfaces.RealInput SOC "Measured SOC of battery"
          annotation (Placement(transformation(extent={{-140,20},{-100,60}})));
        Modelica.Blocks.Interfaces.RealInput Pnet "Net metered power"
          annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
        Modelica.Blocks.Interfaces.RealInput yCharge "Charging signal"
          annotation (Placement(transformation(extent={{100,20},{140,60}}),
            iconTransformation(extent={{100,20},{140,60}})));
        Modelica.Blocks.Interfaces.RealInput yDischarging "Discharging signal"
          annotation (Placement(transformation(extent={{100,-60},{140,-20}}),
            iconTransformation(extent={{100,-60},{140,-20}})));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                    Diagram(
            coordinateSystem(preserveAspectRatio=false)));
      end Controller;
    end Controllers;

    package Examples
      extends Modelica.Icons.ExamplesPackage;
      model BatteryTest
        extends Modelica.Icons.Example;

        Modelica.Blocks.Sources.Pulse uCharge(
          offset=0,
          period=3600*6,
          startTime=3600*3,
          amplitude=0.5)
          annotation (Placement(transformation(extent={{-60,0},{-40,20}})));
        Modelica.Blocks.Sources.Pulse uDischarge(
          offset=0,
          period=3600*6,
          startTime=0,
          amplitude=0.5)
          annotation (Placement(transformation(extent={{-60,-30},{-40,-10}})));
        Simple simple(
          Ecap(displayUnit="kWh") = 180000000,
          P_cap_charge=500,
          P_cap_discharge=500,
          SOC_0=1)
          annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,10},{120,30}})));
      Modelica.Blocks.Interfaces.RealOutput Pcharge "Battery charging power"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Interfaces.RealOutput Pdischarge
        "Battery discharging power"
        annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
      equation
        connect(uCharge.y, simple.uCharge) annotation (Line(points={{-39,10},{
                -30,10},{-30,-4},{-12,-4}}, color={0,0,127}));
        connect(uDischarge.y, simple.uDischarge) annotation (Line(points={{-39,
                -20},{-30,-20},{-30,-8},{-12,-8}}, color={0,0,127}));
      connect(simple.SOC, SOC) annotation (Line(points={{11.2,0},{76,0},{76,20},
              {110,20}}, color={0,0,127}));
      connect(simple.Pcharge, Pcharge) annotation (Line(points={{11.2,-4},{80,
              -4},{80,0},{110,0}}, color={0,0,127}));
      connect(simple.Pdischarge, Pdischarge) annotation (Line(points={{11.2,-8},
              {80,-8},{80,-20},{110,-20}}, color={0,0,127}));
        annotation (experiment(
            StopTime=86400,
            Interval=300,
            Tolerance=1e-06,
            __Dymola_Algorithm="Cvode"));
      end BatteryTest;

      model FeedbackControl
        extends Modelica.Icons.Example;
        parameter Modelica.SIunits.Energy Ecap = 180000000 "Battery capacity";
        parameter Modelica.SIunits.Power P_cap_charge = 500 "Charging capacity";
        parameter Modelica.SIunits.Power P_cap_discharge = 500 "Discharging capacity";
        Simple simple(
          SOC_0=1,
          P_cap_charge=P_cap_charge,
          P_cap_discharge=P_cap_discharge,
        Ecap(displayUnit="kWh") = Ecap)
          annotation (Placement(transformation(extent={{30,-10},{50,10}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,10},{120,30}})));
      Modelica.Blocks.Interfaces.RealOutput Pcharge "Battery charging power"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Interfaces.RealOutput Pdischarge
        "Battery discharging power"
        annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
        Controllers.Controller controller(
          Ecap=E_cap,
          P_cap_charge=P_cap_charge,
          P_cap_discharge=P_cap_discharge)
          annotation (Placement(transformation(extent={{-20,0},{0,20}})));
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam=
            "/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
          annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus1
                   "Weather data bus"
        annotation (Placement(transformation(extent={{-50,80},{-30,100}})));
      equation
      connect(simple.SOC, SOC) annotation (Line(points={{51.2,0},{86,0},{86,20},{110,20}},
                         color={0,0,127}));
      connect(simple.Pcharge, Pcharge) annotation (Line(points={{51.2,-4},{90,-4},{90,
                0},{110,0}},       color={0,0,127}));
      connect(simple.Pdischarge, Pdischarge) annotation (Line(points={{51.2,-8},{90,-8},
                {90,-20},{110,-20}},       color={0,0,127}));
        connect(controller.yCharge, simple.uCharge) annotation (Line(points={{2,14},{14,
                14},{14,-4},{28,-4}}, color={0,0,127}));
        connect(controller.yDischarging, simple.uDischarge)
          annotation (Line(points={{2,6},{12,6},{12,-8},{28,-8}}, color={0,0,127}));
        connect(simple.SOC, controller.SOC) annotation (Line(points={{51.2,0},{60,0},{
                60,-20},{-30,-20},{-30,14},{-22,14}}, color={0,0,127}));
        connect(weaDat.weaBus, weaBus1) annotation (Line(
            points={{-80,90},{-40,90}},
            color={255,204,51},
            thickness=0.5), Text(
            string="%second",
            index=1,
            extent={{6,3},{6,3}}));
        connect(weaBus1.cloTim, controller.clockTime) annotation (Line(
            points={{-40,90},{-32,90},{-32,18},{-22,18}},
            color={255,204,51},
            thickness=0.5), Text(
            string="%first",
            index=-1,
            extent={{-6,3},{-6,3}}));
        annotation (experiment(
            StopTime=86400,
            Interval=300,
            Tolerance=1e-06,
            __Dymola_Algorithm="Cvode"));
      end FeedbackControl;
    end Examples;

    package Training
      extends Modelica.Icons.ExamplesPackage;
      model Simple
      import MPC = SolarPlus;
        extends Modelica.Icons.Example;
      MPC.Batteries.Simple simple
        annotation (Placement(transformation(extent={{-10,-8},{10,12}})));
      Modelica.Blocks.Interfaces.RealInput uCharge
        "Control signal for charging"
        annotation (Placement(transformation(extent={{-140,20},{-100,60}})));
      Modelica.Blocks.Interfaces.RealInput uDischarge
        "Control signal for discharging"
        annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      equation
      connect(simple.uCharge, uCharge) annotation (Line(points={{-12,-2},{-26,
              -2},{-26,-2},{-40,-2},{-40,40},{-120,40}}, color={0,0,127}));
      connect(simple.uDischarge, uDischarge) annotation (Line(points={{-12,-6},
              {-40,-6},{-40,-20},{-120,-20}}, color={0,0,127}));
      connect(simple.SOC, SOC) annotation (Line(points={{11.2,2},{30,2},{30,0},
              {110,0}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Simple;
    end Training;
  end Batteries;

  package PV "Package for PV models"
    model Simple
      "A simple PV model that uses single efficiency to account for module and inverter losses"
      parameter Modelica.SIunits.Area A "PV array area";
      parameter Modelica.SIunits.DimensionlessRatio eff=0.20 "Total efficiency of panel";
      Modelica.Blocks.Interfaces.RealInput Iinc
        "Solar irradiation incident on array"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealOutput Pgen(unit="W") "Power genereated by array"
        annotation (Placement(transformation(extent={{100,-12},{124,12}})));
      Modelica.Blocks.Math.Gain gainA(k=A)
        annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
      Modelica.Blocks.Math.Gain gainEff(k=eff)
        annotation (Placement(transformation(extent={{0,-10},{20,10}})));
    equation
      connect(gainA.u, Iinc)
        annotation (Line(points={{-62,0},{-120,0}}, color={0,0,127}));
      connect(gainA.y, gainEff.u)
        annotation (Line(points={{-39,0},{-2,0}}, color={0,0,127}));
      connect(gainEff.y, Pgen)
        annotation (Line(points={{21,0},{112,0}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-48,76},{0,24}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{0,76},{48,24}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{0,24},{48,-28}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-48,24},{0,-28}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{0,-28},{48,-80}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-48,-28},{0,-80}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-250,170},{250,110}},
              textString="%name",
              lineColor={0,0,255})}),                                Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end Simple;

    package Examples
      extends Modelica.Icons.ExamplesPackage;
      model Simple
        extends Modelica.Icons.Example;
        import MPC = SolarPlus;
        MPC.PV.Simple simple(A=10)
          annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam="/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
          annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
        Buildings.BoundaryConditions.WeatherData.Bus weaBus1
                   "Weather data bus"
          annotation (Placement(transformation(extent={{-70,80},{-50,100}})));
        Modelica.Blocks.Interfaces.RealOutput Pgen "Power genereated by array"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      equation
        connect(weaDat.weaBus, weaBus1) annotation (Line(
            points={{-80,90},{-60,90}},
            color={255,204,51},
            thickness=0.5), Text(
            string="%second",
            index=1,
            extent={{6,3},{6,3}}));
        connect(weaBus1.HGloHor, simple.Iinc) annotation (Line(
            points={{-60,90},{-60,0},{-12,0}},
            color={255,204,51},
            thickness=0.5), Text(
            string="%first",
            index=-1,
            extent={{-6,3},{-6,3}}));
        connect(simple.Pgen, Pgen)
          annotation (Line(points={{11.2,0},{110,0}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Simple;
    end Examples;

    package Training
      extends Modelica.Icons.ExamplesPackage;
      model Simple
      import MPC = SolarPlus;
        extends Modelica.Icons.Example;
      MPC.PV.Simple simple
        annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealOutput Pgen "Power genereated by array"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Interfaces.RealInput Iinc
        "Solar irradiation incident on array in W/m2"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      equation
      connect(simple.Pgen, Pgen)
        annotation (Line(points={{11.2,0},{110,0}}, color={0,0,127}));
      connect(simple.Iinc, Iinc)
        annotation (Line(points={{-12,0},{-120,0}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Simple;
    end Training;
  end PV;

  package Building "Package for building models"

    model Whole_Derivative
      extends BaseClasses.Whole_partial;
      parameter Modelica.SIunits.DimensionlessRatio uHeat_0 = 0.0 "Initial heating signal";
      parameter Modelica.SIunits.DimensionlessRatio uCool_0 = 0.0 "Initial cooling signal";
      parameter Modelica.SIunits.DimensionlessRatio uCharge_0 = 0.0 "Initial charging signal";
      parameter Modelica.SIunits.DimensionlessRatio uDischarge_0 = 0.0 "Initial discharging signal";
      Modelica.Blocks.Interfaces.RealInput duHeat
        "Derivative of heating signal input"
        annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
      Modelica.Blocks.Continuous.Integrator intHeat(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uHeat_0)
        annotation (Placement(transformation(extent={{-94,16},{-86,24}})));
      Modelica.Blocks.Continuous.Integrator intCool(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uCool_0)
        annotation (Placement(transformation(extent={{-94,-24},{-86,-16}})));
      Modelica.Blocks.Interfaces.RealInput duCool
        "Derivative of cooling signal input"
        annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
      Modelica.Blocks.Interfaces.RealInput duCharge
        "Derivative of control signal for charging"
        annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
      Modelica.Blocks.Continuous.Integrator intCharge(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uCharge_0)
        annotation (Placement(transformation(extent={{-94,-64},{-86,-56}})));
      Modelica.Blocks.Continuous.Integrator intDischarge(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uDischarge_0)
        annotation (Placement(transformation(extent={{-94,-104},{-86,-96}})));
      Modelica.Blocks.Interfaces.RealInput duDischarge
        "Derivative of control signal for discharging"
        annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
    Modelica.Blocks.Interfaces.RealOutput uDischarge
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-130},{120,-110}})));
    Modelica.Blocks.Interfaces.RealOutput uCharge
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-110},{120,-90}})));
    Modelica.Blocks.Interfaces.RealOutput uCool
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
    Modelica.Blocks.Interfaces.RealOutput uHeat
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
    equation
      connect(duHeat, intHeat.u)
        annotation (Line(points={{-120,20},{-94.8,20}}, color={0,0,127}));
      connect(duCool, intCool.u)
        annotation (Line(points={{-120,-20},{-94.8,-20}}, color={0,0,127}));
      connect(duCharge, intCharge.u) annotation (Line(points={{-120,-60},{-108,-60},
              {-108,-60},{-94.8,-60}}, color={0,0,127}));
      connect(duDischarge, intDischarge.u)
        annotation (Line(points={{-120,-100},{-94.8,-100}}, color={0,0,127}));
      connect(intHeat.y, thermal.uHeat) annotation (Line(points={{-85.6,20},{
            -70,20},{-70,16},{-42,16}},
                                color={0,0,127}));
      connect(thermal.uCool, intCool.y) annotation (Line(points={{-42,12},{-70,
            12},{-70,-20},{-85.6,-20}},
                                 color={0,0,127}));
      connect(battery.uCharge, intCharge.y) annotation (Line(points={{-42,-34},{-70,
              -34},{-70,-60},{-85.6,-60}}, color={0,0,127}));
      connect(battery.uDischarge, intDischarge.y) annotation (Line(points={{-42,-38},
              {-60,-38},{-60,-100},{-85.6,-100}}, color={0,0,127}));
      connect(intHeat.y, uHeat) annotation (Line(points={{-85.6,20},{-70,20},{-70,6},
              {-50,6},{-50,-60},{110,-60}}, color={0,0,127}));
      connect(intCool.y, uCool) annotation (Line(points={{-85.6,-20},{-70,-20},{-70,
              2},{-52,2},{-52,-80},{110,-80}}, color={0,0,127}));
      connect(intCharge.y, uCharge) annotation (Line(points={{-85.6,-60},{-70,-60},{
              -70,-34},{-54,-34},{-54,-100},{110,-100}}, color={0,0,127}));
      connect(intDischarge.y, uDischarge) annotation (Line(points={{-85.6,-100},{-60,
              -100},{-60,-120},{110,-120}}, color={0,0,127}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)));
    end Whole_Derivative;

    model Whole_Inputs
      extends BaseClasses.Whole_partial(
                                pv(A=300), battery(
        Ecap=626400000,
        P_cap_charge=109000,
        P_cap_discharge=109000));
    Modelica.Blocks.Interfaces.RealInput uHeat "Heating signal input"
      annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
    Modelica.Blocks.Interfaces.RealInput uCool "Cooling signal input"
      annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
    Modelica.Blocks.Interfaces.RealInput uCharge "Control signal for charging"
      annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
    Modelica.Blocks.Interfaces.RealInput uDischarge
      "Control signal for discharging"
      annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
      Modelica.Blocks.Interfaces.RealOutput J
      "Objective function for optimization"
      annotation (Placement(transformation(extent={{100,-190},{120,-170}})));
    Modelica.Blocks.Math.Product squareHeat
      annotation (Placement(transformation(extent={{42,-156},{48,-150}})));
    Modelica.Blocks.Math.Product squareCool
      annotation (Placement(transformation(extent={{42,-166},{48,-160}})));
    Modelica.Blocks.Math.Gain gainDischarge(k=10)
      annotation (Placement(transformation(extent={{54,-186},{60,-180}})));
    Modelica.Blocks.Math.Product squareCharge
      annotation (Placement(transformation(extent={{42,-176},{48,-170}})));
    Modelica.Blocks.Math.Product squareDischarge
      annotation (Placement(transformation(extent={{42,-186},{48,-180}})));
    Modelica.Blocks.Math.Gain gainCharge(k=10)
      annotation (Placement(transformation(extent={{54,-176},{60,-170}})));
    Modelica.Blocks.Math.Gain gainCool(k=1000)
      annotation (Placement(transformation(extent={{54,-166},{60,-160}})));
    Modelica.Blocks.Math.Gain gainHeat(k=1000)
      annotation (Placement(transformation(extent={{54,-156},{60,-150}})));
      Modelica.Blocks.Math.MultiSum sumJ(nu=8, k={1,1,1,1,1,1,1,1})
      annotation (Placement(transformation(extent={{78,-186},{90,-174}})));
    Modelica.Blocks.Interfaces.RealInput uRef
      "Cooling signal input for refrigerator"
      annotation (Placement(transformation(extent={{-140,-160},{-100,-120}})));
    Modelica.Blocks.Interfaces.RealInput uFreDef
      "Defrost signal input for freezer"
      annotation (Placement(transformation(extent={{-140,-200},{-100,-160}})));
    Modelica.Blocks.Interfaces.RealInput uFreCool
      "Cooling signal input for freezer"
      annotation (Placement(transformation(extent={{-140,-240},{-100,-200}})));
    Modelica.Blocks.Math.Gain gainDischarge1(
                                            k=10)
      annotation (Placement(transformation(extent={{54,-196},{60,-190}})));
    Modelica.Blocks.Math.Product squareDischarge1
      annotation (Placement(transformation(extent={{42,-196},{48,-190}})));
    Modelica.Blocks.Math.Gain gainDischarge2(
                                            k=10)
      annotation (Placement(transformation(extent={{54,-206},{60,-200}})));
    Modelica.Blocks.Math.Product squareDischarge2
      annotation (Placement(transformation(extent={{42,-206},{48,-200}})));
    Modelica.Blocks.Math.Gain gainDischarge3(
                                            k=10)
      annotation (Placement(transformation(extent={{54,-216},{60,-210}})));
    Modelica.Blocks.Math.Product squareDischarge3
      annotation (Placement(transformation(extent={{42,-216},{48,-210}})));
    equation
    connect(thermal.uHeat, uHeat) annotation (Line(points={{-42,16},{-80,16},{-80,20},
              {-120,20}},   color={0,0,127}));
    connect(thermal.uCool, uCool) annotation (Line(points={{-42,12},{-94,12},{-94,-20},
              {-120,-20}},    color={0,0,127}));
    connect(battery.uCharge, uCharge) annotation (Line(points={{-42,-34},{-86,-34},{
              -86,-60},{-120,-60}},     color={0,0,127}));
    connect(battery.uDischarge, uDischarge) annotation (Line(points={{-42,-38},{-82,
              -38},{-82,-100},{-120,-100}},    color={0,0,127}));
    connect(squareDischarge.y, gainDischarge.u)
      annotation (Line(points={{48.3,-183},{53.4,-183}},
                                                       color={0,0,127}));
    connect(squareCharge.y, gainCharge.u)
      annotation (Line(points={{48.3,-173},{53.4,-173}},
                                                       color={0,0,127}));
    connect(squareCool.y, gainCool.u)
      annotation (Line(points={{48.3,-163},{53.4,-163}},
                                                       color={0,0,127}));
    connect(squareHeat.y, gainHeat.u)
      annotation (Line(points={{48.3,-153},{53.4,-153}},
                                                       color={0,0,127}));
    connect(gainHeat.y, sumJ.u[1]) annotation (Line(points={{60.3,-153},{64,
            -153},{66,-153},{66,-154},{66,-176},{72,-176},{72,-176.325},{78,
            -176.325}},               color={0,0,127}));
    connect(gainCool.y, sumJ.u[2]) annotation (Line(points={{60.3,-163},{62,
            -163},{62,-164},{64,-164},{64,-177.375},{78,-177.375}},
                                color={0,0,127}));
    connect(gainCharge.y, sumJ.u[3]) annotation (Line(points={{60.3,-173},{62,
            -173},{62,-174},{62,-174},{62,-178.425},{78,-178.425}},
                                           color={0,0,127}));
    connect(gainDischarge.y, sumJ.u[4]) annotation (Line(points={{60.3,-183},{
            62,-183},{62,-184},{62,-184},{62,-182},{62,-182},{62,-179.475},{78,
            -179.475}},                    color={0,0,127}));
    connect(sumJ.y, J) annotation (Line(points={{91.02,-180},{110,-180}},
                       color={0,0,127}));
    connect(uHeat, squareHeat.u1) annotation (Line(points={{-120,20},{-98,20},{-98,6},
              {-98,6},{-98,-151.2},{41.4,-151.2}},    color={0,0,127}));
    connect(squareHeat.u2, squareHeat.u1) annotation (Line(points={{41.4,-154.8},{20,
              -154.8},{20,-151.2},{41.4,-151.2}},color={0,0,127}));
    connect(uCool, squareCool.u1) annotation (Line(points={{-120,-20},{-94,-20},{-94,
              -20},{-94,-20},{-94,-161.2},{41.4,-161.2}},
                                                       color={0,0,127}));
    connect(squareCool.u2, squareCool.u1) annotation (Line(points={{41.4,-164.8},{20,
              -164.8},{20,-161.2},{41.4,-161.2}},color={0,0,127}));
    connect(uCharge, squareCharge.u1) annotation (Line(points={{-120,-60},{-90,-60},
              {-90,-60},{-86,-60},{-86,-171.2},{41.4,-171.2}},  color={0,0,127}));
    connect(squareCharge.u2, squareCharge.u1) annotation (Line(points={{41.4,-174.8},
              {20,-174.8},{20,-171.2},{41.4,-171.2}},   color={0,0,127}));
    connect(uDischarge, squareDischarge.u1) annotation (Line(points={{-120,-100},{-82,
              -100},{-82,-181.2},{41.4,-181.2}},  color={0,0,127}));
    connect(squareDischarge.u2, squareDischarge.u1) annotation (Line(points={{41.4,-184.8},
              {20,-184.8},{20,-181.2},{41.4,-181.2}},        color={0,0,127}));
    connect(thermal.uRef, uRef) annotation (Line(points={{-42,8},{-90,8},{-90,-20},{
              -90,-20},{-90,-140},{-120,-140}},     color={0,0,127}));
    connect(thermal.uFreDef, uFreDef) annotation (Line(points={{-42,4},{-78,4},{-78,
              -180},{-120,-180}},    color={0,0,127}));
    connect(thermal.uFreCool, uFreCool) annotation (Line(points={{-42,0},{-74,0},{-74,
              -220},{-120,-220}},    color={0,0,127}));
    connect(squareDischarge1.y, gainDischarge1.u)
      annotation (Line(points={{48.3,-193},{53.4,-193}},
                                                       color={0,0,127}));
    connect(squareDischarge2.y, gainDischarge2.u)
      annotation (Line(points={{48.3,-203},{53.4,-203}},
                                                       color={0,0,127}));
    connect(squareDischarge3.y, gainDischarge3.u)
      annotation (Line(points={{48.3,-213},{53.4,-213}}, color={0,0,127}));
    connect(gainDischarge1.y, sumJ.u[5]) annotation (Line(points={{60.3,-193},{
            62,-193},{62,-194},{64,-194},{64,-180},{72,-180},{72,-180.525},{78,
            -180.525}},                         color={0,0,127}));
    connect(gainDischarge2.y, sumJ.u[6]) annotation (Line(points={{60.3,-203},{
            62,-203},{62,-204},{66,-204},{66,-181.575},{78,-181.575}},
                                                color={0,0,127}));
    connect(gainDischarge3.y, sumJ.u[7]) annotation (Line(points={{60.3,-213},{
            64,-213},{64,-214},{68,-214},{68,-182.625},{78,-182.625}},
                                                 color={0,0,127}));
    connect(uRef, squareDischarge1.u1) annotation (Line(points={{-120,-140},{-90,-140},
              {-90,-140},{-90,-140},{-90,-191.2},{41.4,-191.2}},       color={0,
            0,127}));
    connect(squareDischarge1.u2, squareDischarge1.u1) annotation (Line(points={{41.4,
              -194.8},{20,-194.8},{20,-191.2},{41.4,-191.2}}, color={0,0,127}));
    connect(uFreDef, squareDischarge2.u1) annotation (Line(points={{-120,-180},{-78,
              -180},{-78,-202},{-4,-202},{-4,-201.2},{41.4,-201.2}},
                                                  color={0,0,127}));
    connect(squareDischarge2.u2, squareDischarge2.u1) annotation (Line(points={{41.4,
              -204.8},{20,-204.8},{20,-201.2},{41.4,-201.2}},   color={0,0,127}));
    connect(uFreCool, squareDischarge3.u1) annotation (Line(points={{-120,-220},{0,-220},
              {0,-211.2},{41.4,-211.2}},        color={0,0,127}));
    connect(squareDischarge3.u2, squareDischarge3.u1) annotation (Line(points={{41.4,
              -214.8},{20,-214.8},{20,-211.2},{41.4,-211.2}},     color={0,0,
            127}));
    connect(multiSum.y, sumJ.u[8]) annotation (Line(points={{93.02,-60},{96,-60},
            {96,-94},{74,-94},{74,-183.675},{78,-183.675}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Bitmap(extent={{-90,-110},{92,-4}}, fileName=
                  "modelica://SolarPlus/StoreFigure.png"),
            Text(
              extent={{-250,170},{250,110}},
              textString="%name",
              lineColor={0,0,255})}),                                Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end Whole_Inputs;

    package Examples
      extends Modelica.Icons.ExamplesPackage;
      model PulseInputs
        extends Modelica.Icons.Example
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      Whole_Inputs store
        annotation (Placement(transformation(extent={{-10,28},{10,60}})));
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam=
            "/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
          annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus1
                   "Weather data bus"
        annotation (Placement(transformation(extent={{-50,80},{-30,100}})));
      Modelica.Blocks.Sources.Pulse rtu_heat(amplitude=1, period=3600*8)
        annotation (Placement(transformation(extent={{-100,30},{-80,50}})));
      Modelica.Blocks.Sources.Pulse rtu_cool(
        amplitude=1,
        period=3600*8,
        startTime=3600*4)
        annotation (Placement(transformation(extent={{-100,0},{-80,20}})));
      Modelica.Blocks.Sources.Pulse batt_charge(amplitude=1, period=3600*8)
        annotation (Placement(transformation(extent={{-100,-30},{-80,-10}})));
      Modelica.Blocks.Sources.Pulse batt_discharge(
        amplitude=1,
        period=3600*8,
        startTime=3600*4)
        annotation (Placement(transformation(extent={{-100,-60},{-80,-40}})));
      Modelica.Blocks.Sources.Pulse ref_cool(amplitude=1, period=3600*8)
        annotation (Placement(transformation(extent={{-100,-90},{-80,-70}})));
      Modelica.Blocks.Sources.Pulse fre_cool(
        amplitude=1,
        period=3600*8,
        startTime=3600*4)
        annotation (Placement(transformation(extent={{-100,-150},{-80,-130}})));
      Modelica.Blocks.Sources.Constant fre_defrost(k=0)
        annotation (Placement(transformation(extent={{-100,-120},{-80,-100}})));
      equation
      connect(weaDat.weaBus, weaBus1) annotation (Line(
          points={{-80,90},{-40,90}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%second",
          index=1,
          extent={{6,3},{6,3}}));
      connect(weaBus1.HGloHor, store.weaHGloHor) annotation (Line(
          points={{-40,90},{-40,60},{-12,60}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(weaBus1.TDryBul, store.weaTDryBul) annotation (Line(
          points={{-40,90},{-40,56},{-12,56}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(rtu_heat.y, store.uHeat) annotation (Line(points={{-79,40},{-44,
              40},{-44,52},{-12,52}}, color={0,0,127}));
      connect(rtu_cool.y, store.uCool) annotation (Line(points={{-79,10},{-42,
              10},{-42,48},{-12,48}}, color={0,0,127}));
      connect(batt_charge.y, store.uCharge) annotation (Line(points={{-79,-20},
              {-40,-20},{-40,44},{-12,44}}, color={0,0,127}));
      connect(batt_discharge.y, store.uDischarge) annotation (Line(points={{-79,
              -50},{-38,-50},{-38,40},{-12,40}}, color={0,0,127}));
      connect(ref_cool.y, store.uRef) annotation (Line(points={{-79,-80},{-36,
              -80},{-36,36},{-12,36}}, color={0,0,127}));
      connect(fre_cool.y, store.uFreCool) annotation (Line(points={{-79,-140},{
              -32,-140},{-32,28},{-12,28}}, color={0,0,127}));
      connect(fre_defrost.y, store.uFreDef) annotation (Line(points={{-79,-110},
              {-34,-110},{-34,32},{-12,32}}, color={0,0,127}));
      annotation (experiment(
          StopTime=86400,
          Interval=300,
          Tolerance=1e-06,
          __Dymola_Algorithm="Cvode"));
      end PulseInputs;

      model FeedbackControl
        extends Modelica.Icons.Example;
      Whole_Inputs store
        annotation (Placement(transformation(extent={{-10,28},{10,60}})));
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam=
            "/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
          annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus1
                   "Weather data bus"
        annotation (Placement(transformation(extent={{-50,80},{-30,100}})));
      Modelica.Blocks.Sources.Constant rtu_cool_set(k=273.15 + 22.2)
        annotation (Placement(transformation(extent={{-100,30},{-80,50}})));
      HVACR.Controllers.SingleStageCoolingController ref_control(deadband=1.5)
        annotation (Placement(transformation(extent={{-60,-8},{-40,12}})));
      Modelica.Blocks.Sources.Constant ref_set(k=273.15 + 3)
        annotation (Placement(transformation(extent={{-100,-2},{-80,18}})));
      HVACR.Controllers.SingleStageCoolingController fre_control(deadband=1.5)
        annotation (Placement(transformation(extent={{-60,-40},{-40,-20}})));
      Modelica.Blocks.Sources.Constant fre_set(k=273.15 - 25)
        annotation (Placement(transformation(extent={{-100,-34},{-80,-14}})));
      Modelica.Blocks.Sources.Constant off(k=0)
        annotation (Placement(transformation(extent={{-100,-80},{-80,-60}})));
      HVACR.Controllers.TwoStageCoolingController rtu_cool_control
        annotation (Placement(transformation(extent={{-60,24},{-40,44}})));
      HVACR.Controllers.SingleStageHeatingController rtu_heat_control
        annotation (Placement(transformation(extent={{-66,54},{-46,74}})));
      Modelica.Blocks.Sources.Constant rtu_heat_set(k=273.15 + 20)
        annotation (Placement(transformation(extent={{-100,60},{-80,80}})));
      equation
      connect(weaDat.weaBus, weaBus1) annotation (Line(
          points={{-80,90},{-40,90}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%second",
          index=1,
          extent={{6,3},{6,3}}));
      connect(weaBus1.HGloHor, store.weaHGloHor) annotation (Line(
          points={{-40,90},{-40,60},{-12,60}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(weaBus1.TDryBul, store.weaTDryBul) annotation (Line(
          points={{-40,90},{-40,56},{-12,56}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(ref_set.y, ref_control.Tset)
        annotation (Line(points={{-79,8},{-62,8}}, color={0,0,127}));
      connect(store.Tref, ref_control.Tmeas) annotation (Line(points={{11,38},{
              18,38},{18,-10},{-68,-10},{-68,-2},{-62,-2}}, color={0,0,127}));
      connect(fre_set.y, fre_control.Tset)
        annotation (Line(points={{-79,-24},{-62,-24}}, color={0,0,127}));
      connect(store.Tfre, fre_control.Tmeas) annotation (Line(points={{11,36},{
              20,36},{20,-42},{-68,-42},{-68,-34},{-62,-34}}, color={0,0,127}));
      connect(ref_control.y, store.uRef) annotation (Line(points={{-39,2},{-26,
              2},{-26,36},{-12,36}}, color={0,0,127}));
      connect(fre_control.y, store.uFreCool) annotation (Line(points={{-39,-30},
              {-24,-30},{-24,28},{-12,28}}, color={0,0,127}));
      connect(off.y, store.uCharge) annotation (Line(points={{-79,-70},{-20,-70},
              {-20,44},{-12,44}}, color={0,0,127}));
      connect(off.y, store.uDischarge) annotation (Line(points={{-79,-70},{-20,
              -70},{-20,40},{-12,40}}, color={0,0,127}));
      connect(store.uFreDef, store.uCharge) annotation (Line(points={{-12,32},{
              -20,32},{-20,44},{-12,44}}, color={0,0,127}));
      connect(rtu_cool_set.y, rtu_cool_control.Tset)
        annotation (Line(points={{-79,40},{-62,40}}, color={0,0,127}));
      connect(store.Trtu, rtu_cool_control.Tmeas) annotation (Line(points={{11,
              42},{16,42},{16,22},{-68,22},{-68,30},{-62,30}}, color={0,0,127}));
      connect(rtu_cool_control.y, store.uCool) annotation (Line(points={{-39,34},
              {-32,34},{-32,48},{-12,48}}, color={0,0,127}));
      connect(rtu_heat_set.y, rtu_heat_control.Tset)
        annotation (Line(points={{-79,70},{-68,70}}, color={0,0,127}));
      connect(rtu_heat_control.Tmeas, rtu_cool_control.Tmeas) annotation (Line(
            points={{-68,60},{-74,60},{-74,50},{-68,50},{-68,30},{-62,30}},
            color={0,0,127}));
      connect(rtu_heat_control.y, store.uHeat) annotation (Line(points={{-45,64},
              {-32,64},{-32,52},{-12,52}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)),
        experiment(
          StartTime=7776000,
          StopTime=7948800,
          Interval=300,
          Tolerance=1e-06,
          __Dymola_Algorithm="Cvode"));
      end FeedbackControl;

      model OpenLoopControl
        extends Modelica.Icons.Example;
      Whole_Inputs store
        annotation (Placement(transformation(extent={{-10,28},{10,60}})));
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam=
            "/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
          annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus1
                   "Weather data bus"
        annotation (Placement(transformation(extent={{-50,80},{-30,100}})));
      Modelica.Blocks.Sources.Constant off(k=0)
        annotation (Placement(transformation(extent={{-100,-80},{-80,-60}})));
      Modelica.Blocks.Interfaces.RealInput uCool "Cooling signal input"
        annotation (Placement(transformation(extent={{-140,20},{-100,60}})));
      Modelica.Blocks.Interfaces.RealInput uRef
        "Cooling signal input for refrigerator"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealInput uFreCool
        "Cooling signal input for freezer"
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      equation
      connect(weaDat.weaBus, weaBus1) annotation (Line(
          points={{-80,90},{-40,90}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%second",
          index=1,
          extent={{6,3},{6,3}}));
      connect(weaBus1.HGloHor, store.weaHGloHor) annotation (Line(
          points={{-40,90},{-40,60},{-12,60}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(weaBus1.TDryBul, store.weaTDryBul) annotation (Line(
          points={{-40,90},{-40,56},{-12,56}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(off.y, store.uCharge) annotation (Line(points={{-79,-70},{-20,-70},
              {-20,44},{-12,44}}, color={0,0,127}));
      connect(off.y, store.uDischarge) annotation (Line(points={{-79,-70},{-20,
              -70},{-20,40},{-12,40}}, color={0,0,127}));
      connect(store.uFreDef, store.uCharge) annotation (Line(points={{-12,32},{
              -20,32},{-20,44},{-12,44}}, color={0,0,127}));
      connect(store.uHeat, store.uCharge) annotation (Line(points={{-12,52},{
              -20,52},{-20,44},{-12,44}}, color={0,0,127}));
      connect(store.uCool, uCool) annotation (Line(points={{-12,48},{-70,48},{
              -70,40},{-120,40}}, color={0,0,127}));
      connect(store.uRef, uRef) annotation (Line(points={{-12,36},{-60,36},{-60,
              0},{-120,0}}, color={0,0,127}));
      connect(store.uFreCool, uFreCool) annotation (Line(points={{-12,28},{-40,
              28},{-40,-40},{-120,-40}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)),
        experiment(
          StartTime=15465600,
          StopTime=15638400,
          Interval=300,
          Tolerance=1e-06,
          __Dymola_Algorithm="Cvode"));
      end OpenLoopControl;
    end Examples;

    package Training
      extends Modelica.Icons.ExamplesPackage;
      model Thermal
        extends Modelica.Icons.Example;
      SolarPlus.Building.BaseClasses.Thermal thermal
          annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul
        "Outside air temperature"
        annotation (Placement(transformation(extent={{-140,80},{-100,120}})));
        Modelica.Blocks.Interfaces.RealInput uCool "Cooling signal input for RTU"
        annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Defrost signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
        Modelica.Blocks.Interfaces.RealInput uRef
          "Cooling signal input for refrigerator"
          annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
          "Cooling signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre(unit="W") "Freezer power"
          annotation (Placement(transformation(extent={{100,-50},{120,-30}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre(unit="K") "Freezer air temperature"
          annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
        Modelica.Blocks.Interfaces.RealOutput Pref(unit="W") "Refrigerator power"
          annotation (Placement(transformation(extent={{100,10},{120,30}})));
        Modelica.Blocks.Interfaces.RealOutput Tref(unit="K") "Refrigerator air temperature"
          annotation (Placement(transformation(extent={{100,30},{120,50}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu(unit="W") "RTU power"
          annotation (Placement(transformation(extent={{100,70},{120,90}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu(unit="K") "Zone air temperature"
          annotation (Placement(transformation(extent={{100,90},{120,110}})));
      Modelica.Blocks.Sources.Constant const(k=0)
        annotation (Placement(transformation(extent={{-100,50},{-80,70}})));
      equation
      connect(weaTDryBul, thermal.Tout) annotation (Line(points={{-120,100},{-60,
              100},{-60,10},{-12,10}}, color={0,0,127}));
      connect(uCool, thermal.uCool) annotation (Line(points={{-120,20},{-86,20},
              {-86,2},{-12,2}}, color={0,0,127}));
      connect(uRef, thermal.uRef) annotation (Line(points={{-120,-20},{-86,-20},
              {-86,-2},{-12,-2}}, color={0,0,127}));
      connect(uFreDef, thermal.uFreDef) annotation (Line(points={{-120,-60},{
              -80,-60},{-80,-6},{-12,-6}}, color={0,0,127}));
      connect(uFreCool, thermal.uFreCool) annotation (Line(points={{-120,-100},
              {-60,-100},{-60,-10},{-12,-10}}, color={0,0,127}));
      connect(thermal.Trtu, Trtu) annotation (Line(points={{11,10},{40,10},{40,
              100},{110,100}}, color={0,0,127}));
      connect(thermal.Prtu, Prtu) annotation (Line(points={{11,8},{60,8},{60,80},
              {110,80}}, color={0,0,127}));
      connect(Tref, thermal.Tref) annotation (Line(points={{110,40},{80,40},{80,
              4},{11,4}}, color={0,0,127}));
      connect(Pref, thermal.Pref) annotation (Line(points={{110,20},{92,20},{92,
              2},{11,2}}, color={0,0,127}));
      connect(Tfre, thermal.Tfre) annotation (Line(points={{110,-20},{80,-20},{
              80,-2},{11,-2}}, color={0,0,127}));
      connect(Pfre, thermal.Pfre) annotation (Line(points={{110,-40},{60,-40},{
              60,-4},{11,-4}}, color={0,0,127}));
      connect(const.y, thermal.uHeat) annotation (Line(points={{-79,60},{-70,60},
              {-70,6},{-12,6}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Thermal;
    end Training;

    package BaseClasses
      partial model Whole_partial
        parameter Modelica.SIunits.Temperature Trtu_0 = 21+273.15 "Initial temperature of rtu zone";
        parameter Modelica.SIunits.Temperature Tref_0 = 3.5+273.15 "Initial temperature of ref zone";
        parameter Modelica.SIunits.Temperature Tfre_0 = -25+273.15 "Initial temperature of fre zone";
        parameter Modelica.SIunits.DimensionlessRatio SOC_0 = 0.5 "Initial SOC of battery";
        Thermal thermal(
          Trtu_0=Trtu_0,
          Tref_0=Tref_0,
          Tfre_0=Tfre_0)
        annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
        Batteries.Simple battery(
          Ecap(displayUnit="kWh") = 21600000,
          P_cap_charge=1000,
          P_cap_discharge=1000,
        SOC_0=SOC_0)
          annotation (Placement(transformation(extent={{-40,-40},{-20,-20}})));
        PV.Simple pv(A=5)
          annotation (Placement(transformation(extent={{-40,70},{-20,90}})));
        Modelica.Blocks.Interfaces.RealInput weaHGloHor
        "Global horizontal irradiation"
          annotation (Placement(transformation(extent={{-140,80},{-100,120}})));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul
        "Outside air drybulb temperature"
          annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet
          annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
        Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
          annotation (Placement(transformation(extent={{100,-110},{120,-90}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu "Rtu zone air temperature"
        annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
        Modelica.Blocks.Math.Gain gainPVGen(k=-1)
          annotation (Placement(transformation(extent={{28,94},{40,106}})));
        Modelica.Blocks.Interfaces.RealOutput Ppv "Power generated by PV system"
          annotation (Placement(transformation(extent={{100,90},{120,110}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu
        "RTU electrical power consumption"
        annotation (Placement(transformation(extent={{100,70},{120,90}})));
        Modelica.Blocks.Interfaces.RealOutput Pcharge
          "Battery charging power consumption"
          annotation (Placement(transformation(extent={{100,10},{120,30}})));
        Modelica.Blocks.Interfaces.RealOutput Pdischarge
          "Battery discharging power generation"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
        Modelica.Blocks.Math.Gain gainBatteryGen(k=-1)
          annotation (Placement(transformation(extent={{28,-6},{40,6}})));
      Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
        annotation (Placement(transformation(extent={{100,-130},{120,-110}})));
      Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
        annotation (Placement(transformation(extent={{100,30},{120,50}})));
      Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
        annotation (Placement(transformation(extent={{100,-150},{120,-130}})));
      Modelica.Blocks.Math.MultiSum multiSum(                   nu=6, k={1,1,1,
            1,1,1})
        annotation (Placement(transformation(extent={{80,-66},{92,-54}})));
      equation
        connect(pv.Iinc, weaHGloHor) annotation (Line(points={{-42,80},{-50,80},{-50,100},
                {-120,100}},          color={0,0,127}));
        connect(thermal.Tout, weaTDryBul) annotation (Line(points={{-42,20},{-60,20},{
                -60,60},{-80,60},{-80,60},{-120,60}},      color={0,0,127}));
        connect(battery.SOC, SOC) annotation (Line(points={{-18.8,-30},{-12,-30},{-12,
                -100},{110,-100}},    color={0,0,127}));
      connect(thermal.Trtu, Trtu) annotation (Line(points={{-19,20},{10,20},{10,
              -80},{110,-80}}, color={0,0,127}));
        connect(pv.Pgen, gainPVGen.u)
          annotation (Line(points={{-18.8,80},{-10,80},{-10,100},{26.8,100}},
                                                           color={0,0,127}));
        connect(gainPVGen.y, Ppv) annotation (Line(points={{40.6,100},{110,100}},
                                 color={0,0,127}));
      connect(thermal.Prtu, Prtu) annotation (Line(points={{-19,18},{-4,18},{-4,80},{110,
                80}},        color={0,0,127}));
        connect(battery.Pcharge, Pcharge) annotation (Line(points={{-18.8,-34},{18,-34},
                {18,20},{110,20}},         color={0,0,127}));
        connect(battery.Pdischarge, gainBatteryGen.u)
          annotation (Line(points={{-18.8,-38},{20,-38},{20,0},{26.8,0}},
                                                            color={0,0,127}));
        connect(gainBatteryGen.y, Pdischarge) annotation (Line(points={{40.6,0},{110,0}},
                                            color={0,0,127}));
      connect(thermal.Tref, Tref) annotation (Line(points={{-19,14},{8,14},{8,-120},{110,
                -120}},                          color={0,0,127}));
      connect(thermal.Pref, Pref) annotation (Line(points={{-19,12},{0,12},{0,60},{110,
                60}},                        color={0,0,127}));
      connect(thermal.Pfre, Pfre) annotation (Line(points={{-19,6},{4,6},{4,40},{110,40}},
                         color={0,0,127}));
      connect(thermal.Tfre, Tfre) annotation (Line(points={{-19,8},{6,8},{6,-140},{110,
                -140}},                          color={0,0,127}));
      connect(gainPVGen.y, multiSum.u[1]) annotation (Line(points={{40.6,100},{50,100},
                {50,-56.5},{80,-56.5}},   color={0,0,127}));
      connect(Prtu, Prtu)
        annotation (Line(points={{110,80},{110,80}}, color={0,0,127}));
      connect(multiSum.u[2], Prtu) annotation (Line(points={{80,-57.9},{52,-57.9},{52,
                80},{110,80}},  color={0,0,127}));
      connect(multiSum.u[3], Pref) annotation (Line(points={{80,-59.3},{54,-59.3},{54,
                60},{110,60}},  color={0,0,127}));
      connect(multiSum.u[4], Pfre) annotation (Line(points={{80,-60.7},{56,-60.7},{56,
                40},{110,40}},                   color={0,0,127}));
      connect(multiSum.u[5], Pcharge) annotation (Line(points={{80,-62.1},{80,-62},{58,
                -62},{58,20},{110,20}},color={0,0,127}));
      connect(multiSum.u[6], Pdischarge) annotation (Line(points={{80,-63.5},{80,-62},
                {60,-62},{60,0},{110,0}},    color={0,0,127}));
      connect(multiSum.y, Pnet)
        annotation (Line(points={{93.02,-60},{110,-60}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,-220},
                  {100,100}}),                                      graphics={
                Rectangle(
                extent={{-100,100},{100,-220}},
                lineColor={0,0,0},
                fillColor={175,175,175},
                fillPattern=FillPattern.Solid)}),                    Diagram(
            coordinateSystem(preserveAspectRatio=false, extent={{-100,-220},{100,100}})));
      end Whole_partial;

      model Thermal
        parameter Modelica.SIunits.HeatCapacity Crtu=1e6 "Heat capacity of RTU zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rrtu=0.0004 "Thermal resistance of RTU zone to outside" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUHeatingCap = 15000 "Heating capacity of RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUCoolingCap = 16998 "Cooling capacity of RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUHeatingEff = 0.99 "Heating efficiency of RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUCoolingCOP = 3 "Cooling COP of RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Temperature Trtu_0 = 21+273.15 "Initial temperature of store" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.HeatCapacity Cref=1e6 "Heat capacity of refrigerator zone" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.ThermalResistance Rref=0.007 "Thermal resistance of refrigerator zone to RTU zone" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.Power RefCoolingCap = 5861 "Cooling capacity of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.Power RefCoolingCOP = 3 "Cooling COP of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.Temperature Tref_0 = 3.5+273.15 "Initial temperature of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.HeatCapacity Cfre=3e6 "Heat capacity of freezer zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.ThermalResistance Rfre=0.008 "Thermal resistance of freezer zone to RTU zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreCoolingCap = 6096 "Cooling capacity of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreHeatingCap = 2000 "Defrost heating capacity of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreHeatingEff = 0.99 "Heating efficiency of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreCoolingCOP = 3 "Cooling COP of frezzer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Temperature Tfre_0 = -25+273.15 "Initial temperature of freezer" annotation(Dialog(group = "Freezer"));

        Envelope.R1C1 rtuZone(Tzone_0=Trtu_0,
          C=Crtu,
          R=Rrtu)
          annotation (Placement(transformation(extent={{-4,80},{16,100}})));
      HVACR.SimpleHeaterCooler RTU1(
        heatingCap=RTUHeatingCap,
        coolingCap=RTUCoolingCap,
        coolingCOP=RTUCoolingCOP,
        heatingEff=RTUHeatingEff)
        annotation (Placement(transformation(extent={{-70,70},{-50,90}})));
        Modelica.Blocks.Interfaces.RealInput Tout "Adjacent temperature"
        annotation (Placement(transformation(extent={{-140,80},{-100,120}})));
        Modelica.Blocks.Interfaces.RealInput uCool "Cooling signal input for RTU"
        annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
        Modelica.Blocks.Interfaces.RealInput uHeat "Heating signal input"
        annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu(unit="K") "Zone air temperature"
          annotation (Placement(transformation(extent={{100,90},{120,110}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu(unit="W") "RTU power"
          annotation (Placement(transformation(extent={{100,70},{120,90}})));
        Envelope.R1C1 refZone(Tzone_0=Tref_0,
          C=Cref,
          R=Rref)
          annotation (Placement(transformation(extent={{40,20},{60,40}})));
        Modelica.Blocks.Interfaces.RealOutput Tref(unit="K") "Refrigerator air temperature"
          annotation (Placement(transformation(extent={{100,30},{120,50}})));
      HVACR.SimpleHeaterCooler refCooler(
        heatingCap=0,
        coolingCap=RefCoolingCap,
        coolingCOP=RefCoolingCOP)
        annotation (Placement(transformation(extent={{-10,10},{10,30}})));
        Modelica.Blocks.Interfaces.RealOutput Pref(unit="W") "Refrigerator power"
          annotation (Placement(transformation(extent={{100,10},{120,30}})));
        Modelica.Blocks.Math.Add addRef
          annotation (Placement(transformation(extent={{50,-10},{70,10}})));
        Modelica.Blocks.Sources.Constant uRefHeat(k=0)
          annotation (Placement(transformation(extent={{-60,10},{-40,30}})));
        Modelica.Blocks.Interfaces.RealInput uRef
          "Cooling signal input for refrigerator"
          annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
        Envelope.R1C1 freZone(Tzone_0=Tfre_0,
          C=Cfre,
          R=Rfre)
          annotation (Placement(transformation(extent={{40,-40},{60,-20}})));
        Modelica.Blocks.Math.Add addFre
          annotation (Placement(transformation(extent={{50,-70},{70,-50}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre(unit="W") "Freezer power"
          annotation (Placement(transformation(extent={{100,-50},{120,-30}})));
      HVACR.SimpleHeaterCooler freCooler(
        coolingCap=FreCoolingCap,
        heatingCap=FreHeatingCap,
        heatingEff=FreHeatingEff,
        coolingCOP=FreCoolingCOP)
        annotation (Placement(transformation(extent={{-10,-50},{10,-30}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
          "Cooling signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Defrost signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre(unit="K") "Freezer air temperature"
          annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
      Buildings.HeatTransfer.Sources.PrescribedTemperature preTout
        annotation (Placement(transformation(extent={{-40,90},{-20,110}})));
      Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTrtu
        annotation (Placement(transformation(extent={{70,90},{90,110}})));
      Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTref
        annotation (Placement(transformation(extent={{70,30},{90,50}})));
      Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTfre
        annotation (Placement(transformation(extent={{70,-30},{90,-10}})));
        Modelica.Blocks.Sources.Constant gamingHeat(k=10000)
          annotation (Placement(transformation(extent={{-78,40},{-58,60}})));
        Modelica.Blocks.Math.Add add
          annotation (Placement(transformation(extent={{-36,78},{-26,88}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu "RTU gas power"
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      equation
        connect(RTU1.qCool, rtuZone.qCool) annotation (Line(points={{-49,76},{-22,76},
                {-22,82},{-6,82}},  color={0,0,127}));
        connect(RTU1.uCool, uCool) annotation (Line(points={{-72,72},{-80,72},{-80,20},
                {-120,20}}, color={0,0,127}));
        connect(RTU1.uHeat, uHeat) annotation (Line(points={{-72,88},{-90,88},{-90,60},
                {-120,60}}, color={0,0,127}));
        connect(refCooler.qCool, refZone.qCool) annotation (Line(points={{11,16},{32,16},
                {32,22},{38,22}}, color={0,0,127}));
        connect(addRef.y, Pref)
          annotation (Line(points={{71,0},{80,0},{80,20},{110,20}},
                                                    color={0,0,127}));
        connect(refCooler.PCool, addRef.u2) annotation (Line(points={{11,12},{24,12},{
                24,-6},{48,-6}}, color={0,0,127}));
        connect(refCooler.PHeat, addRef.u1)
          annotation (Line(points={{11,22},{26,22},{26,6},{48,6}}, color={0,0,127}));
        connect(refCooler.qHeat, refZone.qHeat)
          annotation (Line(points={{11,26},{38,26}}, color={0,0,127}));
        connect(uRefHeat.y, refCooler.uHeat) annotation (Line(points={{-39,20},{-22,20},
                {-22,28},{-12,28}}, color={0,0,127}));
        connect(refCooler.uCool, uRef) annotation (Line(points={{-12,12},{-20,12},{-20,
                -20},{-120,-20}}, color={0,0,127}));
        connect(addFre.y, Pfre)
          annotation (Line(points={{71,-60},{80,-60},{80,-40},{110,-40}},
                                                        color={0,0,127}));
        connect(uFreDef, freCooler.uHeat) annotation (Line(points={{-120,-60},{-60,-60},
                {-60,-32},{-12,-32}}, color={0,0,127}));
        connect(freCooler.uCool, uFreCool) annotation (Line(points={{-12,-48},{-40,-48},
                {-40,-100},{-120,-100}}, color={0,0,127}));
        connect(freCooler.qHeat, freZone.qHeat)
          annotation (Line(points={{11,-34},{38,-34}}, color={0,0,127}));
        connect(freCooler.qCool, freZone.qCool) annotation (Line(points={{11,-44},{32,
                -44},{32,-38},{38,-38}}, color={0,0,127}));
        connect(freCooler.PHeat, addFre.u1) annotation (Line(points={{11,-38},{26,-38},
                {26,-54},{48,-54}}, color={0,0,127}));
        connect(freCooler.PCool, addFre.u2) annotation (Line(points={{11,-48},{24,-48},
                {24,-66},{48,-66}}, color={0,0,127}));
        connect(Tfre, Tfre)
          annotation (Line(points={{110,-20},{110,-20}}, color={0,0,127}));
      connect(Tout, preTout.T)
        annotation (Line(points={{-120,100},{-42,100}}, color={0,0,127}));
      connect(preTout.port, rtuZone.port_adj) annotation (Line(points={{-20,100},{-16,
                100},{-16,96},{-4,96}},     color={191,0,0}));
      connect(rtuZone.port_cap, senTrtu.port) annotation (Line(points={{6.2,90},{20,90},
                {20,100},{70,100}},       color={191,0,0}));
      connect(senTrtu.T, Trtu)
        annotation (Line(points={{90,100},{110,100}}, color={0,0,127}));
      connect(rtuZone.port_cap, refZone.port_adj) annotation (Line(points={{6.2,90},{20,
                90},{20,36},{40,36}},       color={191,0,0}));
      connect(rtuZone.port_cap, freZone.port_adj) annotation (Line(points={{6.2,90},{20,
                90},{20,-24},{40,-24}},       color={191,0,0}));
      connect(refZone.port_cap, senTref.port) annotation (Line(points={{50.2,30},
              {66,30},{66,40},{70,40}}, color={191,0,0}));
      connect(senTref.T, Tref)
        annotation (Line(points={{90,40},{110,40}}, color={0,0,127}));
      connect(freZone.port_cap, senTfre.port) annotation (Line(points={{50.2,
              -30},{66,-30},{66,-20},{70,-20}}, color={191,0,0}));
      connect(senTfre.T, Tfre)
        annotation (Line(points={{90,-20},{110,-20}}, color={0,0,127}));
      connect(Tref, Tref) annotation (Line(points={{110,40},{105,40},{105,40},{
              110,40}}, color={0,0,127}));
      connect(Trtu, Trtu) annotation (Line(points={{110,100},{104,100},{104,100},
              {110,100}}, color={0,0,127}));
        connect(gamingHeat.y, add.u2) annotation (Line(points={{-57,50},{-40,50},{-40,
                80},{-37,80}}, color={0,0,127}));
        connect(RTU1.qHeat, add.u1)
          annotation (Line(points={{-49,86},{-37,86}}, color={0,0,127}));
        connect(add.y, rtuZone.qHeat) annotation (Line(points={{-25.5,83},{-22.75,83},
                {-22.75,86},{-6,86}}, color={0,0,127}));
      connect(RTU1.PCool, Prtu) annotation (Line(points={{-49,72},{80,72},{80,
              80},{110,80}}, color={0,0,127}));
      connect(RTU1.PHeat, Grtu) annotation (Line(points={{-49,82},{-44,82},{-44,
              60},{110,60}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
              Text(
                extent={{-250,170},{250,110}},
                textString="%name",
                lineColor={0,0,255}),
            Rectangle(
              extent={{-92,88},{90,-88}},
              lineColor={0,0,0},
              fillColor={212,212,212},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-72,52},{-16,12}},
              lineColor={0,0,0},
              fillColor={166,166,166},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-16,52},{74,12}},
              lineColor={0,0,0},
              fillColor={166,166,166},
              fillPattern=FillPattern.Solid),
            Line(
              points={{0,-32},{74,-32},{74,82},{74,96},{100,96}},
              color={0,0,0},
              pattern=LinePattern.Dot),
            Ellipse(
              extent={{16,38},{32,22}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{16,36},{32,26}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              textString="T"),
            Line(
              points={{32,30},{88,30},{88,40},{100,40}},
              color={0,0,0},
              pattern=LinePattern.Dot),
            Line(
              points={{-46,24},{-46,-20},{100,-20}},
              color={0,0,0},
              pattern=LinePattern.Dot),
            Ellipse(
              extent={{-54,38},{-38,22}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-54,36},{-38,26}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              textString="T"),
            Text(
              extent={{-10,-26},{6,-36}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              textString="T"),
            Ellipse(
              extent={{-10,-24},{6,-40}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-10,-26},{6,-36}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              textString="T")}),                                     Diagram(
            coordinateSystem(preserveAspectRatio=false)));
      end Thermal;
    end BaseClasses;
  end Building;

annotation (uses(Modelica(version="3.2.2"), Buildings(version="5.0.0")));
end SolarPlus;