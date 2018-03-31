within SolarPlusMPC;
package Envelope "Package for envelope thermal response models"
  model R1C1 "Zone thermal model"
    parameter Modelica.SIunits.HeatCapacity C=1e5 "Heat capacity of zone";
    parameter Modelica.SIunits.ThermalResistance R=0.01 "Thermal resistance of zone";
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor capAir(C=C)
      annotation (Placement(transformation(extent={{-10,0},{10,20}})));
  Modelica.Thermal.HeatTransfer.Components.ThermalResistor resAdj(R=R)
      annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
    Modelica.Thermal.HeatTransfer.Sources.PrescribedTemperature preAdj
      annotation (Placement(transformation(extent={{-70,-10},{-50,10}})));
    Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow preHeat
      annotation (Placement(transformation(extent={{-58,-50},{-38,-30}})));
    Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow preCool
      annotation (Placement(transformation(extent={{-58,-70},{-38,-50}})));
    Modelica.Blocks.Interfaces.RealInput Tadj "Adjacent temperature"
      annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
    Modelica.Blocks.Interfaces.RealInput qHeat "Heat floww for heating"
      annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
    Modelica.Blocks.Interfaces.RealInput qCool "Heat flow for cooling"
      annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
    Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor temperatureSensor
      annotation (Placement(transformation(extent={{42,-10},{62,10}})));
    Modelica.Blocks.Interfaces.RealOutput Tzone "Zone air temperature"
      annotation (Placement(transformation(extent={{100,-10},{120,10}})));
  equation
    connect(resAdj.port_b, capAir.port)
      annotation (Line(points={{-20,0},{0,0}}, color={191,0,0}));
    connect(preAdj.port, resAdj.port_a)
      annotation (Line(points={{-50,0},{-40,0}}, color={191,0,0}));
    connect(preHeat.port, capAir.port)
      annotation (Line(points={{-38,-40},{0,-40},{0,0}}, color={191,0,0}));
    connect(preCool.port, capAir.port)
      annotation (Line(points={{-38,-60},{0,-60},{0,0}}, color={191,0,0}));
    connect(preAdj.T, Tadj) annotation (Line(points={{-72,0},{-80,0},{-80,60},{-120,
            60}}, color={0,0,127}));
    connect(qHeat, preHeat.Q_flow)
      annotation (Line(points={{-120,-40},{-58,-40}}, color={0,0,127}));
    connect(qCool, preCool.Q_flow) annotation (Line(points={{-120,-80},{-80,-80},{
            -80,-60},{-58,-60}}, color={0,0,127}));
    connect(capAir.port, temperatureSensor.port)
      annotation (Line(points={{0,0},{42,0}}, color={191,0,0}));
    connect(temperatureSensor.T, Tzone)
      annotation (Line(points={{62,0},{110,0}}, color={0,0,127}));
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
        Line(points={{100,0},{2,0}}, color={0,0,0},
            pattern=LinePattern.Dot)}),
                              Diagram(coordinateSystem(preserveAspectRatio=
            false)));
  end R1C1;

end Envelope;
