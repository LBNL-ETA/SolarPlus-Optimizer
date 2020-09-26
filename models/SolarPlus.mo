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
      extends Modelica.Icons.Package;
      model R1C1
      import MPC = SolarPlus;

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
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
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
          annotation (Placement(transformation(extent={{-20,-10},{0,10}})));
        Modelica.Blocks.Math.BooleanToReal booleanToReal
          annotation (Placement(transformation(extent={{30,-10},{50,10}})));
        Modelica.Blocks.Interfaces.RealOutput y "Controller output"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
        Modelica.Blocks.MathBoolean.Not not1
          annotation (Placement(transformation(extent={{10,-4},{18,4}})));
        Modelica.Blocks.Logical.LessThreshold greaterThreshold(threshold=0.5)
          annotation (Placement(transformation(extent={{-10,-42},{10,-22}})));
        Modelica.Blocks.Logical.Switch switch1
          annotation (Placement(transformation(extent={{74,-10},{94,10}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Connector of Boolean input signal" annotation (Placement(
              transformation(extent={{-140,-100},{-100,-60}})));
        Modelica.Blocks.Sources.Constant const(k=0)
          annotation (Placement(transformation(extent={{28,-66},{48,-46}})));
      equation
        connect(Tmeas, onOffController.u) annotation (Line(points={{-120,-40},{
                -60,-40},{-60,-6},{-22,-6}},
                                    color={0,0,127}));
        connect(Tset, onOffController.reference) annotation (Line(points={{-120,60},
                {-60,60},{-60,6},{-22,6}},
                                      color={0,0,127}));
        connect(booleanToReal.u, not1.y)
          annotation (Line(points={{28,0},{18.8,0}}, color={255,0,255}));
        connect(not1.u, onOffController.y)
          annotation (Line(points={{8.4,0},{1,0}},   color={255,0,255}));
        connect(greaterThreshold.u, uFreDef) annotation (Line(points={{-12,-32},
                {-20,-32},{-20,-80},{-120,-80}}, color={0,0,127}));
        connect(booleanToReal.y, switch1.u1) annotation (Line(points={{51,0},{
                60,0},{60,8},{72,8}}, color={0,0,127}));
        connect(greaterThreshold.y, switch1.u2) annotation (Line(points={{11,
                -32},{64,-32},{64,0},{72,0}}, color={255,0,255}));
        connect(const.y, switch1.u3) annotation (Line(points={{49,-56},{68,-56},
                {68,-8},{72,-8}}, color={0,0,127}));
        connect(switch1.y, y)
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
          annotation (Placement(transformation(extent={{-87,-22},{-67,-2}})));
        Modelica.Blocks.Math.Add add
          annotation (Placement(transformation(extent={{-59,-6},{-39,14}})));
        Modelica.Blocks.MathBoolean.Not not2
          annotation (Placement(transformation(extent={{-4,-34},{4,-26}})));
        Modelica.Blocks.Math.BooleanToReal booleanToReal2
          annotation (Placement(transformation(extent={{10,-40},{30,-20}})));
        Modelica.Blocks.Math.Add add1
          annotation (Placement(transformation(extent={{64,-10},{84,10}})));
        Modelica.Blocks.Math.Gain stage2div(k=0.5)
          annotation (Placement(transformation(extent={{37,-40},{57,-20}})));
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
        connect(const.y, add.u2) annotation (Line(points={{-66,-12},{-64,-12},{
                -64,-2},{-61,-2}},
                           color={0,0,127}));
        connect(Tset, add.u1) annotation (Line(points={{-120,60},{-90,60},{-90,
                10},{-61,10}},
                     color={0,0,127}));
        connect(Tmeas, stage2.u) annotation (Line(points={{-120,-40},{-40,-40},{-40,-36},
                {-32,-36}}, color={0,0,127}));
        connect(add.y, stage2.reference) annotation (Line(points={{-38,4},{-36,
                4},{-36,-24},{-32,-24}},
                                 color={0,0,127}));
        connect(stage2.y, not2.u)
          annotation (Line(points={{-9,-30},{-5.6,-30}}, color={255,0,255}));
        connect(not2.y, booleanToReal2.u)
          annotation (Line(points={{4.8,-30},{8,-30}}, color={255,0,255}));
        connect(booleanToReal2.y, stage2div.u)
          annotation (Line(points={{31,-30},{35,-30}}, color={0,0,127}));
        connect(stage1div.y, add1.u1) annotation (Line(points={{9,30},{29,30},{
                29,6},{62,6}}, color={0,0,127}));
        connect(stage2div.y, add1.u2) annotation (Line(points={{58,-30},{60,-30},
                {60,-6},{62,-6}}, color={0,0,127}));
        connect(add1.y, y)
          annotation (Line(points={{85,0},{110,0}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false, grid={1,1}),
                                                                      graphics={
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
              coordinateSystem(preserveAspectRatio=false, grid={1,1})));
      end TwoStageCoolingController;

      model SingleStageHeatingController
        parameter Real deadband = 1 "Deadband of controller";
        Modelica.Blocks.Interfaces.RealInput Tset "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealInput Tmeas "Temperature measured"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
        Modelica.Blocks.Logical.OnOffController onOffController(bandwidth=deadband)
          annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
        Modelica.Blocks.Math.BooleanToReal booleanToReal
          annotation (Placement(transformation(extent={{-20,-10},{0,10}})));
        Modelica.Blocks.Interfaces.RealOutput y "Controller output"
          annotation (Placement(transformation(extent={{100,30},{120,50}})));
        Buildings.Controls.OBC.CDL.Continuous.Hysteresis hys(uLow=273.15 + 21.9,
            uHigh=273.15 + 22.1,
          pre_y_start=true)
          annotation (Placement(transformation(extent={{-20,30},{0,50}})));
        Buildings.Controls.OBC.CDL.Logical.Switch swi
          annotation (Placement(transformation(extent={{40,30},{60,50}})));
        Buildings.Controls.OBC.CDL.Continuous.Sources.Constant con(k=0)
          annotation (Placement(transformation(extent={{-20,70},{0,90}})));
      equation
        connect(Tmeas, onOffController.u) annotation (Line(points={{-120,-40},{
                -80,-40},{-80,-6},{-62,-6}},
                                    color={0,0,127}));
        connect(Tset, onOffController.reference) annotation (Line(points={{-120,60},
                {-80,60},{-80,6},{-62,6}},
                                      color={0,0,127}));
        connect(onOffController.y, booleanToReal.u)
          annotation (Line(points={{-39,0},{-22,0}},
                                                   color={255,0,255}));
        connect(hys.y, swi.u2)
          annotation (Line(points={{1,40},{38,40}}, color={255,0,255}));
        connect(con.y, swi.u1) annotation (Line(points={{1,80},{20,80},{20,48},
                {38,48}}, color={0,0,127}));
        connect(swi.y, y)
          annotation (Line(points={{61,40},{110,40}}, color={0,0,127}));
        connect(booleanToReal.y, swi.u3) annotation (Line(points={{1,0},{20,0},
                {20,32},{38,32}}, color={0,0,127}));
        connect(hys.u, onOffController.reference) annotation (Line(points={{-22,
                40},{-80,40},{-80,6},{-62,6}}, color={0,0,127}));
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
      parameter Modelica.SIunits.Power P_cap "Charging or discharging capacity";
      parameter Modelica.SIunits.DimensionlessRatio eta=1.0 "Charging or discharging efficiency";
      parameter Modelica.SIunits.DimensionlessRatio SOC_0 "Initial state of charge";
      Modelica.SIunits.Energy E(fixed=true,start=SOC_0*Ecap) "Battery energy level";
      Modelica.SIunits.Power P_loss "Charging or discharging losses of battery";
      Modelica.Blocks.Interfaces.RealInput u(min=-1, max=1)
        "Control signal for charging [0,1] and discharging [-1,0]"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,28},{124,52}})));
      Modelica.Blocks.Interfaces.RealOutput Preal(unit="W") "Battery real power"
        annotation (Placement(transformation(extent={{100,-52},{124,-28}})));
    equation
      SOC = E/Ecap;
      der(E) =Preal - P_loss;
      Preal = u*P_cap;
      P_loss =Preal*(1 - eta);
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
        Modelica.Blocks.Interfaces.RealInput y "Battery signal" annotation (
            Placement(transformation(extent={{80,-20},{120,20}}),
              iconTransformation(extent={{80,-20},{120,20}})));
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

      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,10},{120,30}})));
      Modelica.Blocks.Interfaces.RealOutput Preal "Battery charging power"
          annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
        Buildings.Controls.OBC.CDL.Continuous.Sources.Sine sin(freqHz=1/1800)
          annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
        Simple simple(
          Ecap(displayUnit="kWh") = 626400000,
          P_cap=109000,
          SOC_0=0.5)
          annotation (Placement(transformation(extent={{0,-10},{20,10}})));
      equation
        connect(sin.y, simple.u)
          annotation (Line(points={{-38,0},{-2,0}}, color={0,0,127}));
        connect(simple.SOC, SOC) annotation (Line(points={{21.2,4},{60,4},{60,
                20},{110,20}}, color={0,0,127}));
        connect(simple.Preal, Preal) annotation (Line(points={{21.2,-4},{60,-4},
                {60,-20},{110,-20}}, color={0,0,127}));
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
      Modelica.Blocks.Interfaces.RealOutput Pbattery "Battery power"
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
      connect(simple.SOC, SOC) annotation (Line(points={{51.2,4},{80,4},{80,20},
                {110,20}},
                         color={0,0,127}));
        connect(simple.Pcharge, Pbattery) annotation (Line(points={{51.2,-4},{
                80,-4},{80,-20},{110,-20}}, color={0,0,127}));
        connect(simple.SOC, controller.SOC) annotation (Line(points={{51.2,4},{
                60,4},{60,-20},{-30,-20},{-30,14},{-22,14}},
                                                      color={0,0,127}));
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
        connect(controller.y, simple.u) annotation (Line(points={{0,10},{18,10},
                {18,0},{28,0}}, color={0,0,127}));
        connect(controller.Pnet, Pbattery) annotation (Line(points={{-22,10},{
                -42,10},{-42,-52},{80,-52},{80,-20},{110,-20}}, color={0,0,127}));
        annotation (experiment(
            StopTime=86400,
            Interval=300,
            Tolerance=1e-06,
            __Dymola_Algorithm="Cvode"));
      end FeedbackControl;
    end Examples;

    package Training
      extends Modelica.Icons.Package;
      model Simple
      import MPC = SolarPlus;

      MPC.Batteries.Simple simple
        annotation (Placement(transformation(extent={{0,-10},{20,10}})));
      Modelica.Blocks.Interfaces.RealInput uBattery
          "Control signal for battery"
          annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      equation
      connect(simple.SOC, SOC) annotation (Line(points={{21.2,4},{30,4},{30,0},
                {110,0}},
                        color={0,0,127}));
        connect(uBattery, simple.u)
          annotation (Line(points={{-120,0},{-2,0}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Simple;
    end Training;

    model Emulator "Emulator model of the battery"
      Simple simple(
        Ecap(displayUnit="kWh") = 145800000,
        P_cap(displayUnit="kW") = 21000,
        eta=1.0,
        SOC_0=0.5)
        annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
      Modelica.Blocks.Math.Gain gain(k=1/14000)
        annotation (Placement(transformation(extent={{-80,-10},{-60,10}})));
      Modelica.Blocks.Interfaces.RealInput PSet
        "Power setpoint from the controller" annotation (Placement(
            transformation(extent={{-140,-20},{-100,20}}), iconTransformation(
              extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealOutput SOC_meas
        "Measured state of charge from the emulator" annotation (Placement(
            transformation(extent={{160,-10},{180,10}}), iconTransformation(
              extent={{100,-50},{120,-30}})));
      Modelica.Blocks.Logical.LessEqualThreshold SOCmin(threshold=0.25)
        "minimum state of charge"
        annotation (Placement(transformation(extent={{0,-10},{20,10}})));
      Modelica.Blocks.Logical.Switch switch1
        annotation (Placement(transformation(extent={{40,-10},{60,10}})));
      Modelica.Blocks.Sources.Constant const(k=0.25)
        annotation (Placement(transformation(extent={{0,30},{20,50}})));
      Modelica.Blocks.Logical.LessEqualThreshold SOCmin1(threshold=0.95)
        "minimum state of charge"
        annotation (Placement(transformation(extent={{80,-10},{100,10}})));
      Modelica.Blocks.Sources.Constant const1(k=0.95)
        annotation (Placement(transformation(extent={{80,30},{100,50}})));
      Modelica.Blocks.Logical.Switch switch2
        annotation (Placement(transformation(extent={{120,-10},{140,10}})));
      PV.Simple pv(
        A=272.6,
        eff=0.26,
        effDcAc=0.98)
        annotation (Placement(transformation(extent={{-40,-70},{-20,-50}})));
      Modelica.Blocks.Interfaces.RealOutput PPv
        "Power generated by PV system, negative sign"
        annotation (Placement(transformation(extent={{160,-70},{180,-50}}),
            iconTransformation(extent={{100,30},{120,50}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaPv "plane of array solar radiation on pv"
        annotation (Placement(transformation(
              extent={{-140,-80},{-100,-40}}),
                                             iconTransformation(extent={{-140,20},
                {-100,60}})));
    equation
      connect(gain.y, simple.u)
        annotation (Line(points={{-59,0},{-42,0}},color={0,0,127}));
      connect(PSet, gain.u)
        annotation (Line(points={{-120,0},{-82,0}}, color={0,0,127}));
      connect(simple.SOC, SOCmin.u) annotation (Line(points={{-18.8,4},{-10,4},
              {-10,0},{-2,0}}, color={0,0,127}));
      connect(SOCmin.y, switch1.u2)
        annotation (Line(points={{21,0},{38,0}}, color={255,0,255}));
      connect(const.y, switch1.u1) annotation (Line(points={{21,40},{26,40},{26,
              8},{38,8}}, color={0,0,127}));
      connect(simple.SOC, switch1.u3) annotation (Line(points={{-18.8,4},{-10,4},
              {-10,-20},{30,-20},{30,-8},{38,-8}}, color={0,0,127}));
      connect(switch1.y, SOCmin1.u)
        annotation (Line(points={{61,0},{78,0}}, color={0,0,127}));
      connect(SOCmin1.y, switch2.u2)
        annotation (Line(points={{101,0},{118,0}}, color={255,0,255}));
      connect(const1.y, switch2.u3) annotation (Line(points={{101,40},{110,40},
              {110,-8},{118,-8}}, color={0,0,127}));
      connect(switch2.y, SOC_meas)
        annotation (Line(points={{141,0},{170,0}}, color={0,0,127}));
      connect(switch1.y, switch2.u1) annotation (Line(points={{61,0},{70,0},{70,
              -20},{112,-20},{112,8},{118,8}}, color={0,0,127}));
      connect(PPv,PPv)
        annotation (Line(points={{170,-60},{170,-60}},
                                                     color={0,0,127}));
      connect(weaPoaPv,pv. Iinc)
        annotation (Line(points={{-120,-60},{-42,-60}},
                                                      color={0,0,127}));
      connect(pv.Pgen,PPv)
        annotation (Line(points={{-18.8,-60},{170,-60}},
                                                       color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,
                -100},{100,100}}),                                  graphics={
                                    Rectangle(
            extent={{-100,-100},{100,100}},
            lineColor={0,0,127},
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-58,20},{64,-56}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-38,42},{-16,20}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{22,42},{44,20}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-248,168},{252,108}},
              textString="%name",
              lineColor={0,0,255})}),         Diagram(coordinateSystem(
              preserveAspectRatio=false, extent={{-100,-100},{160,100}})));
    end Emulator;
  end Batteries;

  package PV "Package for PV models"
    model Simple
      "A simple PV model that uses single efficiency to account for module and inverter losses"
      parameter Modelica.SIunits.Area A "PV array area";
      parameter Modelica.SIunits.DimensionlessRatio eff=0.20 "Total efficiency of panel";
      parameter Modelica.SIunits.DimensionlessRatio effDcAc=0.8 "Inveter efficiency";
      Modelica.Blocks.Interfaces.RealInput Iinc
        "Solar irradiation incident on array"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealOutput Pgen(unit="W") "Power genereated by array"
        annotation (Placement(transformation(extent={{100,-12},{124,12}})));
      Modelica.Blocks.Math.Gain gainA(k=A)
        annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
      Modelica.Blocks.Math.Gain gainEff(k=eff)
        annotation (Placement(transformation(extent={{-8,-10},{12,10}})));
      Modelica.Blocks.Math.Gain gainEffDcAc(k=effDcAc)
        annotation (Placement(transformation(extent={{40,-10},{60,10}})));
    equation
      connect(gainA.u, Iinc)
        annotation (Line(points={{-62,0},{-120,0}}, color={0,0,127}));
      connect(gainA.y, gainEff.u)
        annotation (Line(points={{-39,0},{-10,0}},color={0,0,127}));
      connect(gainEff.y, gainEffDcAc.u)
        annotation (Line(points={{13,0},{38,0}}, color={0,0,127}));
      connect(gainEffDcAc.y, Pgen)
        annotation (Line(points={{61,0},{112,0}}, color={0,0,127}));
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

      model Simple
      import MPC = SolarPlus;

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
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Simple;
    end Training;

  end PV;

  package Building "Package for building models"

    package Examples
      extends Modelica.Icons.ExamplesPackage;
      model PulseInputs
        extends Modelica.Icons.Example
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
        SolarPlus.Building.BaseClasses.Whole_Inputs store
          annotation (Placement(transformation(extent={{-10,28},{10,60}})));
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam=
              "/home/kun/Documents/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
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
      Modelica.Blocks.Sources.Pulse ref_cool(amplitude=1, period=3600*8)
        annotation (Placement(transformation(extent={{-100,-90},{-80,-70}})));
      Modelica.Blocks.Sources.Pulse fre_cool(
        amplitude=1,
        period=3600*8,
        startTime=3600*4)
        annotation (Placement(transformation(extent={{-100,-150},{-80,-130}})));
      Modelica.Blocks.Sources.Constant fre_defrost(k=0)
        annotation (Placement(transformation(extent={{-100,-120},{-80,-100}})));
        Buildings.Controls.OBC.CDL.Continuous.Sources.Sine sin(freqHz=1/1800)
          annotation (Placement(transformation(extent={{-100,-40},{-80,-20}})));
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
          points={{-40,90},{-40,60},{-12,60}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
        connect(rtu_heat.y, store.uHeat) annotation (Line(points={{-79,40},{-44,
                40},{-44,48},{-12,48}}, color={0,0,127}));
        connect(rtu_cool.y, store.uCool) annotation (Line(points={{-79,10},{-42,
                10},{-42,44},{-12,44}}, color={0,0,127}));
      connect(ref_cool.y, store.uRef) annotation (Line(points={{-79,-80},{-36,
              -80},{-36,36},{-12,36}}, color={0,0,127}));
      connect(fre_cool.y, store.uFreCool) annotation (Line(points={{-79,-140},{
              -32,-140},{-32,28},{-12,28}}, color={0,0,127}));
      connect(fre_defrost.y, store.uFreDef) annotation (Line(points={{-79,-110},
              {-34,-110},{-34,32},{-12,32}}, color={0,0,127}));
        connect(sin.y, store.uBattery) annotation (Line(points={{-78,-30},{-40,
                -30},{-40,40},{-12,40}}, color={0,0,127}));
      annotation (experiment(
          StopTime=86400,
          Interval=300,
          Tolerance=1e-06,
          __Dymola_Algorithm="Cvode"));
      end PulseInputs;

      model OpenLoopControl
        extends Modelica.Icons.Example;
        SolarPlus.Building.BaseClasses.Whole_Inputs store
          annotation (Placement(transformation(extent={{-10,28},{10,60}})));
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam=
              "/home/kun/Documents/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
          annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus1
                   "Weather data bus"
        annotation (Placement(transformation(extent={{-50,80},{-30,100}})));
      Modelica.Blocks.Sources.Constant off(k=0)
        annotation (Placement(transformation(extent={{-60,20},{-40,40}})));
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
          points={{-40,90},{-40,59},{-11,59}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
        connect(off.y, store.uFreDef) annotation (Line(points={{-39,30},{-20,30},
                {-20,32},{-11,32}},       color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)),
        experiment(
          StartTime=15465600,
          StopTime=15638400,
          Interval=300,
          Tolerance=1e-06,
          __Dymola_Algorithm="Cvode"));
      end OpenLoopControl;

      model FeedbackControl
        import SolarPlus;
        extends Modelica.Icons.Example;
        extends SolarPlus.Building.BaseClasses.Supervisory;
        Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(
            computeWetBulbTemperature=false, filNam=
              "/home/kun/Documents/SolarPlus-Optimizer/models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
          annotation (Placement(transformation(extent={{-100,120},{-80,140}})));
      Modelica.Blocks.Sources.Constant rtu_heat_set(k=273.15 + 21)
        annotation (Placement(transformation(extent={{-100,60},{-80,80}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus1
                   "Weather data bus"
        annotation (Placement(transformation(extent={{-50,120},{-30,140}})));
      Modelica.Blocks.Sources.Constant rtu_cool_set(k=273.15 + 22.2)
        annotation (Placement(transformation(extent={{-100,30},{-80,50}})));
      Modelica.Blocks.Sources.Constant ref_set(k=273.15 + 3)
        annotation (Placement(transformation(extent={{-100,0},{-80,20}})));
      Modelica.Blocks.Sources.Constant fre_set(k=273.15 - 25)
        annotation (Placement(transformation(extent={{-100,-30},{-80,-10}})));
      Modelica.Blocks.Sources.Constant off(k=0)
        annotation (Placement(transformation(extent={{-100,-100},{-80,-80}})));
      Modelica.Blocks.Sources.Pulse fre_def(
          startTime=3*3600,
          width=5,
          period=6*3600)
          annotation (Placement(transformation(extent={{-100,-70},{-80,-50}})));
      equation
        connect(weaDat.weaBus, weaBus1) annotation (Line(
            points={{-80,130},{-40,130}},
            color={255,204,51},
            thickness=0.5), Text(
            string="%second",
            index=1,
            extent={{6,3},{6,3}}));
        connect(rtu_heat_set.y, rtu_heat_control.Tset)
          annotation (Line(points={{-79,70},{-62,70}}, color={0,0,127}));
        connect(rtu_cool_set.y, rtu_cool_control.Tset)
          annotation (Line(points={{-79,40},{-62,40}}, color={0,0,127}));
        connect(ref_set.y, ref_control.Tset)
          annotation (Line(points={{-79,10},{-62,10}}, color={0,0,127}));
        connect(weaBus1.HGloHor, store.weaHGloHor) annotation (Line(
            points={{-40,130},{-22,130},{-22,60},{-12,60}},
            color={255,204,51},
            thickness=0.5), Text(
            string="%first",
            index=-1,
            extent={{-6,3},{-6,3}}));
        connect(weaBus1.TDryBul, store.weaTDryBul) annotation (Line(
            points={{-40,130},{-22,130},{-22,59},{-11,59}},
            color={255,204,51},
            thickness=0.5), Text(
            string="%first",
            index=-1,
            extent={{-6,3},{-6,3}}));
        connect(store.uBattery, off.y) annotation (Line(points={{-11,38},{-22,
                38},{-22,-90},{-79,-90}}, color={0,0,127}));
        connect(fre_def.y, store.uFreDef) annotation (Line(points={{-79,-60},{
                -18,-60},{-18,32},{-11,32}}, color={0,0,127}));
        connect(fre_set.y, fre_control.Tset)
          annotation (Line(points={{-79,-20},{-62,-20}}, color={0,0,127}));
        connect(fre_def.y, fre_control.uFreDef) annotation (Line(points={{-79,
                -60},{-72,-60},{-72,-34},{-62,-34}}, color={0,0,127}));
        connect(off.y, ref_control.uFreDef) annotation (Line(points={{-79,-90},
                {-76,-90},{-76,-4},{-62,-4}}, color={0,0,127}));
      end FeedbackControl;

    end Examples;

    package Emulation
      extends Modelica.Icons.Package;
      model Store
        extends BaseClasses.Supervisory(ref_control(deadband=1));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul
          "Outside air drybulb temperature"
          annotation (Placement(transformation(extent={{-140,120},{-100,160}}),
              iconTransformation(extent={{-120,70},{-100,90}})));
        Modelica.Blocks.Interfaces.RealInput setHeat "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,42},{-100,82}}),
              iconTransformation(extent={{-120,10},{-100,30}})));
        Modelica.Blocks.Interfaces.RealInput setCool "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,16},{-100,56}}),
              iconTransformation(extent={{-120,-10},{-100,10}})));
        Modelica.Blocks.Interfaces.RealInput setRef "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,-12},{-100,28}}),
              iconTransformation(extent={{-120,-30},{-100,-10}})));
        Modelica.Blocks.Interfaces.RealInput setFre "Temperature setpoint"
          annotation (Placement(transformation(extent={{-140,-40},{-100,0}}),
              iconTransformation(extent={{-120,-50},{-100,-30}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Defrost signal input for freezer" annotation (Placement(
              transformation(extent={{-140,-70},{-100,-30}}), iconTransformation(
                extent={{-120,-70},{-100,-50}})));
        Modelica.Blocks.Interfaces.RealInput uBattery "Battery input signal"
          annotation (Placement(transformation(extent={{-140,-100},{-100,-60}}),
              iconTransformation(extent={{-120,-90},{-100,-70}})));
        Modelica.Blocks.Interfaces.RealOutput Ppv "Power generated by PV system"
          annotation (Placement(transformation(extent={{100,90},{120,110}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu
        "RTU electrical power consumption"
        annotation (Placement(transformation(extent={{100,70},{120,90}})));
      Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
        annotation (Placement(transformation(extent={{100,30},{120,50}})));
        Modelica.Blocks.Interfaces.RealOutput Pbattery "Battery power"
          annotation (Placement(transformation(extent={{100,10},{120,30}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu "Gas heating power"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet
          annotation (Placement(transformation(extent={{100,-70},{120,-50}}),
              iconTransformation(extent={{100,-30},{120,-10}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu "Rtu zone air temperature"
        annotation (Placement(transformation(extent={{100,-90},{120,-70}}),
              iconTransformation(extent={{100,-50},{120,-30}})));
        Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
          annotation (Placement(transformation(extent={{100,-110},{120,-90}}),
              iconTransformation(extent={{100,-70},{120,-50}})));
      Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
        annotation (Placement(transformation(extent={{100,-130},{120,-110}}),
              iconTransformation(extent={{100,-90},{120,-70}})));
      Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
        annotation (Placement(transformation(extent={{100,-150},{120,-130}}),
              iconTransformation(extent={{100,-110},{120,-90}})));
        Modelica.Blocks.Sources.Constant uRefDef(k=0) annotation (Placement(
              transformation(extent={{-120,-160},{-100,-140}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaPv
          "Plane of array solar radiation on pv"
          annotation (Placement(transformation(extent={{-140,94},{-100,134}}),
              iconTransformation(extent={{-120,50},{-100,70}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaWin
          "Plane of array solar radiation on windows"
          annotation (Placement(transformation(extent={{-140,68},{-100,108}}),
              iconTransformation(extent={{-120,30},{-100,50}})));
      equation
        connect(store.weaTDryBul, weaTDryBul) annotation (Line(points={{-11,59},
                {-18,59},{-18,140},{-120,140}}, color={0,0,127}));
        connect(setHeat, rtu_heat_control.Tset)
          annotation (Line(points={{-120,62},{-92,62},{-92,70},{-62,70}},
                                                        color={0,0,127}));
        connect(setCool, rtu_cool_control.Tset)
          annotation (Line(points={{-120,36},{-92,36},{-92,40},{-62,40}},
                                                        color={0,0,127}));
        connect(setRef, ref_control.Tset)
          annotation (Line(points={{-120,8},{-92,8},{-92,10},{-62,10}},
                                                        color={0,0,127}));
        connect(setFre, fre_control.Tset)
          annotation (Line(points={{-120,-20},{-62,-20}}, color={0,0,127}));
        connect(uFreDef, store.uFreDef) annotation (Line(points={{-120,-50},{
                -24,-50},{-24,32},{-11,32}}, color={0,0,127}));
        connect(uBattery, store.uBattery) annotation (Line(points={{-120,-80},{
                -20,-80},{-20,38},{-11,38}}, color={0,0,127}));
        connect(Ppv, store.Ppv) annotation (Line(points={{110,100},{20,100},{20,
                58.4},{11,58.4}},
                              color={0,0,127}));
        connect(store.Prtu_west, Prtu) annotation (Line(points={{11,56.4},{24,
                56.4},{24,80},{110,80}},
                                   color={0,0,127}));
        connect(Pref, store.Pref) annotation (Line(points={{110,60},{28,60},{28,
                52.4},{11,52.4}},
                              color={0,0,127}));
        connect(Pfre, store.Pfre) annotation (Line(points={{110,40},{32,40},{32,
                50.4},{11,50.4}},
                              color={0,0,127}));
        connect(Pbattery, store.Pbattery) annotation (Line(points={{110,20},{36,
                20},{36,48.4},{11,48.4}},
                                      color={0,0,127}));
        connect(store.Pnet, Pnet) annotation (Line(points={{11,42.2},{32,42.2},
                {32,-60},{110,-60}},
                                 color={0,0,127}));
        connect(store.Trtu_west, Trtu) annotation (Line(points={{11,40.2},{28,
                40.2},{28,-80},{110,-80}},
                                     color={0,0,127}));
        connect(SOC, store.SOC) annotation (Line(points={{110,-100},{24,-100},{
                24,36.2},{11,36.2}},
                                 color={0,0,127}));
        connect(Tref, store.Tref) annotation (Line(points={{110,-120},{20,-120},
                {20,34.2},{11,34.2}},
                                  color={0,0,127}));
        connect(Tfre, store.Tfre) annotation (Line(points={{110,-140},{16,-140},
                {16,32.2},{11,32.2}},
                                  color={0,0,127}));
        connect(uFreDef, fre_control.uFreDef) annotation (Line(points={{-120,
                -50},{-90,-50},{-90,-34},{-62,-34}}, color={0,0,127}));
        connect(uRefDef.y, ref_control.uFreDef) annotation (Line(points={{-99,
                -150},{-80,-150},{-80,-4},{-62,-4}}, color={0,0,127}));
        connect(store.Grtu_west, Grtu) annotation (Line(points={{11,46.2},{54,
                46.2},{54,0},{110,0}},
                                 color={0,0,127}));
        connect(weaPoaPv, store.weaPoaPv) annotation (Line(points={{-120,114},{
                -22,114},{-22,56},{-11,56}}, color={0,0,127}));
        connect(weaPoaWin, store.weaPoaWin) annotation (Line(points={{-120,88},
                {-26,88},{-26,53},{-11,53}}, color={0,0,127}));
        annotation (Diagram(coordinateSystem(extent={{-100,-160},{100,140}})), Icon(
              graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}));
      end Store;
    end Emulation;

    package Training
      extends Modelica.Icons.Package;
      model Thermal

        SolarPlus.Building.BaseClasses.Thermal thermal(
          Trtu_west_0(displayUnit="K"),
          Trtu_east_0(displayUnit="K"),
          Tref_0(displayUnit="K"),
          Tfre_0(displayUnit="K"))
          annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul "Outside air temperature"
        annotation (Placement(transformation(extent={{-140,80},{-100,120}}),
              iconTransformation(extent={{-120,80},{-100,100}})));
        Modelica.Blocks.Interfaces.RealInput uCoolWest
          "Cooling signal input for RTU west" annotation (Placement(
              transformation(extent={{-140,20},{-100,60}}), iconTransformation(
                extent={{-120,20},{-100,40}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef "Defrost signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-90},{-100,-50}}),
              iconTransformation(extent={{-120,-70},{-100,-50}})));
        Modelica.Blocks.Interfaces.RealInput uRef "Cooling signal input for refrigerator"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}}),
              iconTransformation(extent={{-120,-40},{-100,-20}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool "Cooling signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-120},{-100,-80}}),
              iconTransformation(extent={{-120,-100},{-100,-80}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre(unit="W") "Freezer power"
          annotation (Placement(transformation(extent={{100,-50},{120,-30}}),
              iconTransformation(extent={{100,-100},{120,-80}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre(unit="K") "Freezer air temperature"
          annotation (Placement(transformation(extent={{100,-30},{120,-10}}),
              iconTransformation(extent={{100,-80},{120,-60}})));
        Modelica.Blocks.Interfaces.RealOutput Pref(unit="W") "Refrigerator power"
          annotation (Placement(transformation(extent={{100,-10},{120,10}}),
              iconTransformation(extent={{100,-50},{120,-30}})));
        Modelica.Blocks.Interfaces.RealOutput Tref(unit="K") "Refrigerator air temperature"
          annotation (Placement(transformation(extent={{100,10},{120,30}}),
              iconTransformation(extent={{100,-30},{120,-10}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_west(unit="W")
          "WestRTU power" annotation (Placement(transformation(extent={{100,70},
                  {120,90}}), iconTransformation(extent={{100,60},{120,80}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west(unit="K")
          "West zone air temperature" annotation (Placement(transformation(
                extent={{100,90},{120,110}}), iconTransformation(extent={{100,
                  80},{120,100}})));
        Modelica.Blocks.Sources.Constant uHeat(k=0)
        annotation (Placement(transformation(extent={{-100,46},{-80,66}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaWin "Window solar radiation"
           annotation (Placement(transformation(extent={{-140,54},{-100,94}}),
                                         iconTransformation(extent={{-120,50},{
                  -100,70}})));
        Modelica.Blocks.Interfaces.RealInput uCoolEast
          "Cooling signal input for RTU East" annotation (Placement(
              transformation(extent={{-140,-20},{-100,20}}), iconTransformation(
                extent={{-120,-10},{-100,10}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_east(unit="W")
          "EastRTU power" annotation (Placement(transformation(extent={{100,30},
                  {120,50}}), iconTransformation(extent={{100,10},{120,30}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east(unit="K")
          "East zone air temperature" annotation (Placement(transformation(
                extent={{100,50},{120,70}}), iconTransformation(extent={{100,30},
                  {120,50}})));
      equation
      connect(weaTDryBul, thermal.Tout) annotation (Line(points={{-120,100},{
                -60,100},{-60,9.9},{-10.7,9.9}},
                                       color={0,0,127}));
        connect(uCoolWest, thermal.uCoolWest) annotation (Line(points={{-120,40},
                {-80,40},{-80,2.9},{-10.7,2.9}}, color={0,0,127}));
      connect(uRef, thermal.uRef) annotation (Line(points={{-120,-40},{-86,-40},
                {-86,-4.9},{-10.7,-4.9}},
                                  color={0,0,127}));
      connect(uFreDef, thermal.uFreDef) annotation (Line(points={{-120,-70},{
                -80,-70},{-80,-7.3},{-10.7,-7.3}},
                                           color={0,0,127}));
      connect(uFreCool, thermal.uFreCool) annotation (Line(points={{-120,-100},
                {-60,-100},{-60,-9.9},{-10.7,-9.9}},
                                               color={0,0,127}));
        connect(thermal.Trtu_west, Trtu_west) annotation (Line(points={{10.7,
                9.3},{40,9.3},{40,100},{110,100}}, color={0,0,127}));
        connect(thermal.Prtu_west, Prtu_west) annotation (Line(points={{10.7,
                7.1},{60,7.1},{60,80},{110,80}}, color={0,0,127}));
      connect(Tref, thermal.Tref) annotation (Line(points={{110,20},{80,20},{80,
                -3.5},{10.7,-3.5}},
                          color={0,0,127}));
      connect(Pref, thermal.Pref) annotation (Line(points={{110,0},{92,0},{92,
                -5.5},{10.7,-5.5}},
                          color={0,0,127}));
      connect(Tfre, thermal.Tfre) annotation (Line(points={{110,-20},{80,-20},{
                80,-7.5},{10.7,-7.5}},
                               color={0,0,127}));
      connect(Pfre, thermal.Pfre) annotation (Line(points={{110,-40},{60,-40},{
                60,-9.3},{10.7,-9.3}},
                               color={0,0,127}));
        connect(uHeat.y, thermal.uHeatWest) annotation (Line(points={{-79,56},{
                -70,56},{-70,5.3},{-10.7,5.3}}, color={0,0,127}));
        connect(weaPoaWin, thermal.poaWin) annotation (Line(points={{-120,74},{
                -40,74},{-40,7.7},{-10.7,7.7}}, color={0,0,127}));
        connect(uHeat.y, thermal.uHeatEast) annotation (Line(points={{-79,56},{
                -70,56},{-70,0.5},{-10.7,0.5}}, color={0,0,127}));
        connect(thermal.Trtu_east, Trtu_east) annotation (Line(points={{10.7,
                1.9},{70,1.9},{70,60},{110,60}}, color={0,0,127}));
        connect(thermal.Prtu_east, Prtu_east) annotation (Line(points={{10.7,
                0.1},{74,0.1},{74,40},{110,40}}, color={0,0,127}));
        connect(uCoolEast, thermal.uCoolEast) annotation (Line(points={{-120,0},
                {-88,0},{-88,-1.9},{-10.7,-1.9}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Thermal;

      model Refridgeration

        Modelica.Blocks.Interfaces.RealInput uFreDef "Defrost signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}}),
              iconTransformation(extent={{-120,-40},{-100,-20}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool "Cooling signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-100},{-100,-60}}),
              iconTransformation(extent={{-120,-80},{-100,-60}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre(unit="K")
          "Freezer air temperature"
          annotation (Placement(transformation(extent={{100,30},{120,50}}),
              iconTransformation(extent={{100,30},{120,50}})));
        Modelica.Blocks.Interfaces.RealInput Trtu_east
          "East RTU zone temperature"
          annotation (Placement(transformation(extent={{-140,20},{-100,60}}),
              iconTransformation(extent={{-120,20},{-100,40}})));
        Modelica.Blocks.Interfaces.RealInput Trtu_west
          "RTU west zone temperature" annotation (Placement(transformation(
                extent={{-140,60},{-100,100}}), iconTransformation(extent={{-120,
                  60},{-100,80}})));
        BaseClasses.Refridgeration refridgeration
          annotation (Placement(transformation(extent={{-20,0},{0,20}})));
        Modelica.Blocks.Interfaces.RealInput uRef
          "Cooling signal input for refridgerator" annotation (Placement(
              transformation(extent={{-140,-20},{-100,20}}), iconTransformation(
                extent={{-120,-10},{-100,10}})));
        Modelica.Blocks.Interfaces.RealOutput Tref(unit="K")
          "Freezer air temperature" annotation (Placement(transformation(extent=
                 {{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
      equation
        connect(Trtu_west, refridgeration.Trtu_west) annotation (Line(points={{
                -120,80},{-60,80},{-60,17},{-21,17}}, color={0,0,127}));
        connect(Trtu_east, refridgeration.Trtu_east) annotation (Line(points={{
                -120,40},{-80,40},{-80,14},{-21,14}}, color={0,0,127}));
        connect(uFreDef, refridgeration.uFreDef) annotation (Line(points={{-120,
                -40},{-40,-40},{-40,6},{-21,6}}, color={0,0,127}));
        connect(uFreCool, refridgeration.uFreCool) annotation (Line(points={{
                -120,-80},{-30,-80},{-30,3},{-21,3}}, color={0,0,127}));
        connect(uRef, refridgeration.uRef) annotation (Line(points={{-120,0},{
                -60,0},{-60,10},{-21,10}}, color={0,0,127}));
        connect(refridgeration.Tfre, Tfre) annotation (Line(points={{1,14},{74,
                14},{74,40},{110,40}}, color={0,0,127}));
        connect(refridgeration.Tref, Tref) annotation (Line(points={{1,10},{30,
                10},{30,0},{110,0}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Refridgeration;

      model RTU
        BaseClasses.Rtu rtu(Trtu_west_0(displayUnit="K"), Trtu_east_0(
              displayUnit="K"))
          annotation (Placement(transformation(extent={{-20,0},{0,20}})));
        Modelica.Blocks.Interfaces.RealInput Tout "Outdoor air temperature"
        annotation (Placement(transformation(extent={{-128,46},{-100,74}}),
              iconTransformation(extent={{-114,74},{-100,88}})));
        Modelica.Blocks.Interfaces.RealInput poaWin "Solar radiation on the windows"
          annotation (Placement(transformation(extent={{-128,6},{-100,34}}),
              iconTransformation(extent={{-114,52},{-100,66}})));
        Modelica.Blocks.Interfaces.RealInput uCoolWest
          "Cooling signal input for RTU on the west side" annotation (Placement(
              transformation(extent={{-128,-54},{-100,-26}}),
                                                            iconTransformation(extent={{-114,
                  -28},{-100,-14}})));
        Modelica.Blocks.Interfaces.RealInput uCoolEast
          "Cooling signal input for RTU on the east side" annotation (Placement(
              transformation(extent={{-128,-74},{-100,-46}}),
              iconTransformation(extent={{-114,-76},{-100,-62}})));
        Modelica.Blocks.Sources.Constant uHeat(k=0)
        annotation (Placement(transformation(extent={{-80,-20},{-60,0}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west(unit="K")
          "West zone air temperature" annotation (Placement(transformation(
                extent={{100,50},{120,70}}),   iconTransformation(extent={{100,66},{114,
                  80}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east(unit="K")
          "East zone air temperature" annotation (Placement(transformation(
                extent={{100,-70},{120,-50}}),
                                             iconTransformation(extent={{100,-34},{114,
                  -20}})));
        Modelica.Blocks.Interfaces.RealInput Tref "Outdoor air temperature"
          annotation (Placement(transformation(extent={{-128,78},{-100,106}}),
              iconTransformation(extent={{-114,74},{-100,88}})));
        Modelica.Blocks.Interfaces.RealInput Tfre "Outdoor air temperature"
          annotation (Placement(transformation(extent={{-128,-94},{-100,-66}}),
              iconTransformation(extent={{-114,74},{-100,88}})));
      equation
        connect(Tout, rtu.Tout) annotation (Line(points={{-114,60},{-52,60},{
                -52,16.1},{-20.7,16.1}}, color={0,0,127}));
        connect(poaWin, rtu.poaWin) annotation (Line(points={{-114,20},{-60,20},
                {-60,13.9},{-20.7,13.9}}, color={0,0,127}));
        connect(uCoolWest, rtu.uCoolWest) annotation (Line(points={{-114,-40},{
                -40,-40},{-40,7.9},{-20.7,7.9}}, color={0,0,127}));
        connect(uHeat.y, rtu.uHeatWest) annotation (Line(points={{-59,-10},{-50,
                -10},{-50,11.5},{-20.7,11.5}}, color={0,0,127}));
        connect(rtu.Trtu_west, Trtu_west) annotation (Line(points={{0.7,17.3},{
                80,17.3},{80,60},{110,60}}, color={0,0,127}));
        connect(rtu.Trtu_east, Trtu_east) annotation (Line(points={{0.7,7.3},{
                80,7.3},{80,-60},{110,-60}}, color={0,0,127}));
        connect(uCoolEast, rtu.uCoolEast) annotation (Line(points={{-114,-60},{
                -32,-60},{-32,3.1},{-20.7,3.1}}, color={0,0,127}));
        connect(uHeat.y, rtu.uHeatEast) annotation (Line(points={{-59,-10},{-36,
                -10},{-36,5.5},{-20.7,5.5}}, color={0,0,127}));
        connect(Tfre, rtu.Tfre) annotation (Line(points={{-114,-80},{-26,-80},{
                -26,0.7},{-20.7,0.7}}, color={0,0,127}));
        connect(Tref, rtu.Tref) annotation (Line(points={{-114,92},{-30,92},{
                -30,17.9},{-20.7,17.9}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end RTU;
    end Training;

    package Optimization
      extends Modelica.Icons.Package;

      model Store
        extends BaseClasses.partialStore(store(
            TSpRtuEast=293.65,
            TSpRtuWest=294.65,
            TSpRef=273.15,
            TSpFre=251.15));
        Modelica.Blocks.Interfaces.RealInput uHeat
          "RTU heating signal input"   annotation (Placement(transformation(extent={{-160,30},{-120,70}}),
              iconTransformation(extent={{-160,-40},{-120,0}})));
        Modelica.Blocks.Sources.Constant uFreDef(k=0)
          "Freezer defrost signal" annotation (Placement(
              transformation(extent={{-120,-212},{-100,-192}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_west
          "RTU west gas heating power" annotation (Placement(transformation(
                extent={{120,10},{140,30}}), iconTransformation(extent={{120,
                  -10},{140,10}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_east
          "RTU east gas heating power" annotation (Placement(transformation(
                extent={{120,-10},{140,10}}), iconTransformation(extent={{120,
                  -30},{140,-10}})));
      equation
        connect(uHeat, store.uHeat)   annotation (Line(points={{-140,50},{-11,50}}, color={0,0,127}));
        connect(uHeat, squareHeat.u1) annotation (Line(points={{-140,50},{-102,
                50},{-102,-142},{18,-142},{18,-141.2},{37.4,-141.2}}, color={0,
                0,127}));
        connect(uFreDef.y, squareDischarge2.u1) annotation (Line(points={{-99,
                -202},{-90,-202},{-90,-208},{-24,-208},{-24,-191.2},{37.4,
                -191.2}},
              color={0,0,127}));
        connect(store.uFreDef, squareDischarge2.u1) annotation (Line(points={{-11,32},
                {-74,32},{-74,-192},{-24,-192},{-24,-191.2},{37.4,-191.2}},
              color={0,0,127}));
        connect(store.Grtu_west, Grtu_west) annotation (Line(points={{11,46.2},
                {32,46.2},{32,46},{54,46},{54,20},{130,20}}, color={0,0,127}));
        connect(store.Grtu_east, Grtu_east) annotation (Line(points={{11,44.2},
                {38,44.2},{38,0},{130,0}}, color={0,0,127}));
        annotation (Diagram(coordinateSystem(extent={{-120,-220},{120,140}})));
      end Store;

      model StoreSim
        extends SolarPlus.Building.BaseClasses.partialStore;
        Modelica.Blocks.Sources.Constant const(k=20 + 273.15)
          annotation (Placement(transformation(extent={{-120,-10},{-100,10}})));
        HVACR.Controllers.SingleStageHeatingController
          singleStageHeatingController
          annotation (Placement(transformation(extent={{-50,40},{-30,60}})));
      Modelica.Blocks.Interfaces.RealInput uFreDef "Defrost signal for freezer"
          annotation (Placement(transformation(extent={{-140,-200},{-100,-160}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu
          "Roof top unit heating power output" annotation (Placement(
              transformation(extent={{100,-10},{120,10}}), iconTransformation(
                extent={{100,10},{120,30}})));
      equation
        connect(const.y, singleStageHeatingController.Tset) annotation (Line(
              points={{-99,0},{-88,0},{-88,56},{-52,56}},   color={0,0,127}));
        connect(singleStageHeatingController.y, store.uHeat) annotation (Line(
              points={{-29,54},{-22,54},{-22,50},{-11,50}}, color={0,0,127}));
        connect(store.Trtu_west, singleStageHeatingController.Tmeas)
          annotation (Line(points={{11,40.2},{14,40.2},{14,34},{-56,34},{-56,46},
                {-52,46}},
                      color={0,0,127}));
        connect(uFreDef, squareDischarge2.u1) annotation (Line(points={{-120,
                -180},{-96,-180},{-96,-202},{20,-202},{20,-191.2},{37.4,-191.2}},
              color={0,0,127}));
        connect(store.uFreDef, squareDischarge2.u1) annotation (Line(points={{-11,32},
                {-40,32},{-40,-202},{20,-202},{20,-191.2},{37.4,-191.2}},
              color={0,0,127}));
        connect(singleStageHeatingController.y, squareHeat.u1) annotation (Line(
              points={{-29,54},{-22,54},{-22,-152},{20,-152},{20,-141.2},{37.4,
                -141.2}}, color={0,0,127}));
        connect(store.Grtu_west, Grtu) annotation (Line(points={{11,46.2},{80,
                46.2},{80,0},{110,0}},
                                color={0,0,127}));
      end StoreSim;

      block StoreIsland "This store model is for island mode optimization"
        parameter Modelica.SIunits.Temperature Trtu_west_0 = 21+273.15
          "Initial temperature of rtu west zone";
        parameter Modelica.SIunits.Temperature Trtu_east_0 = 21+273.15
          "Initial temperature of rtu east zone";
        parameter Modelica.SIunits.Temperature Tref_0 = 3.5+273.15
          "Initial temperature of ref zone";
        parameter Modelica.SIunits.Temperature Tfre_0 = -25+273.15
          "Initial temperature of fre zone";
        parameter Modelica.SIunits.Power PBattery = 0
          "Measured battery power";

        BaseClasses.StoreIsland storeIsland(
          Trtu_west_0 = Trtu_west_0,
          Trtu_east_0 = Trtu_east_0,
          Tref_0 = Tref_0,
          Tfre_0 = Tfre_0,
          PBattery = PBattery)
          annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul
          "Outdoor dry bulb temperature" annotation (Placement(transformation(
                extent={{-140,60},{-100,100}}), iconTransformation(extent={{-120,80},
                  {-100,100}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaPv
          "plane of array solar radiation on pv" annotation (Placement(
              transformation(extent={{-140,30},{-100,70}}), iconTransformation(
                extent={{-120,50},{-100,70}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaWin
          "plane of array solar radiation on Windows" annotation (Placement(
              transformation(extent={{-140,0},{-100,40}}), iconTransformation(
                extent={{-120,20},{-100,40}})));
        Modelica.Blocks.Interfaces.RealInput uCool "RTU cooling signal input"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}}),
              iconTransformation(extent={{-120,-40},{-100,-20}})));
        Modelica.Blocks.Interfaces.RealInput uRef
        "Cooling signal input for refrigerator"
        annotation (Placement(transformation(extent={{-140,-90},{-100,-50}}),
              iconTransformation(extent={{-120,-70},{-100,-50}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
        "Cooling signal input for freezer"
        annotation (Placement(transformation(extent={{-140,-120},{-100,-80}}),
              iconTransformation(extent={{-120,-100},{-100,-80}})));
        Modelica.Blocks.Interfaces.RealOutput J annotation (Placement(
              transformation(extent={{100,-56},{120,-36}}),
                                                          iconTransformation(
                extent={{100,-24},{114,-10}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west
          "Rtu zone air temperature" annotation (Placement(transformation(
                extent={{100,-74},{120,-54}}), iconTransformation(extent={{100,-40},
                  {114,-26}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east
          "Rtu zone air temperature" annotation (Placement(transformation(
                extent={{100,-92},{120,-72}}),  iconTransformation(extent={{100,-58},
                  {114,-44}})));
        Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
        annotation (Placement(transformation(extent={{100,-106},{120,-86}}),
              iconTransformation(extent={{100,-78},{114,-64}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
        annotation (Placement(transformation(extent={{100,-120},{120,-100}}),
              iconTransformation(extent={{100,-100},{114,-86}})));
        Modelica.Blocks.Interfaces.RealOutput Ppv "Power generated by PV system"
          annotation (Placement(transformation(extent={{100,74},{120,94}}),
              iconTransformation(extent={{100,86},{114,100}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_west
          "RTU electrical power consumption" annotation (Placement(
              transformation(extent={{100,58},{120,78}}), iconTransformation(
                extent={{100,70},{114,84}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_east
          "RTU electrical power consumption" annotation (Placement(
              transformation(extent={{100,44},{120,64}}), iconTransformation(
                extent={{100,54},{114,68}})));
        Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
        annotation (Placement(transformation(extent={{100,30},{120,50}}),
              iconTransformation(extent={{100,38},{114,52}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
        annotation (Placement(transformation(extent={{100,18},{120,38}}),
              iconTransformation(extent={{100,22},{114,36}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_west "RTU gas power"
          annotation (Placement(transformation(extent={{100,2},{120,22}}),
              iconTransformation(extent={{100,8},{114,22}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_east "RTU gas power"
          annotation (Placement(transformation(extent={{100,-14},{120,6}}),
              iconTransformation(extent={{100,-8},{114,6}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet
          annotation (Placement(transformation(extent={{100,-30},{120,-10}}),
              iconTransformation(extent={{100,-24},{114,-10}})));
        Modelica.Blocks.Interfaces.RealInput uHeat "RTU heating signal input"
          annotation (Placement(transformation(extent={{-140,-30},{-100,10}}),
              iconTransformation(extent={{-120,-10},{-100,10}})));
      equation
        connect(weaTDryBul, storeIsland.weaTDryBul) annotation (Line(points={{-120,80},
                {-88,80},{-88,19},{-41,19}},          color={0,0,127}));
        connect(weaPoaPv, storeIsland.weaPoaPv) annotation (Line(points={{-120,50},
                {-90,50},{-90,16},{-41,16}},     color={0,0,127}));
        connect(weaPoaWin, storeIsland.weaPoaWin) annotation (Line(points={{-120,20},
                {-92,20},{-92,13},{-41,13}},          color={0,0,127}));
        connect(uCool, storeIsland.uCool) annotation (Line(points={{-120,-40},{
                -70,-40},{-70,7},{-41,7}}, color={0,0,127}));
        connect(uRef, storeIsland.uRef) annotation (Line(points={{-120,-70},{
                -66,-70},{-66,4},{-41,4}}, color={0,0,127}));
        connect(uFreCool, storeIsland.uFreCool) annotation (Line(points={{-120,
                -100},{-60,-100},{-60,1},{-41,1}},
                                                 color={0,0,127}));
        connect(storeIsland.Trtu_west, Trtu_west) annotation (Line(points={{-19.3,6.7},
                {-2,6.7},{-2,-64},{110,-64}}, color={0,0,127}));
        connect(storeIsland.Trtu_east, Trtu_east) annotation (Line(points={{-19.3,4.9},
                {-6,4.9},{-6,-82},{110,-82}}, color={0,0,127}));
        connect(storeIsland.Tref, Tref) annotation (Line(points={{-19.3,2.9},{-10,2.9},
                {-10,-96},{110,-96}}, color={0,0,127}));
        connect(storeIsland.Tfre, Tfre) annotation (Line(points={{-19.3,0.7},{-14,0.7},
                {-14,-110},{110,-110}}, color={0,0,127}));
        connect(storeIsland.Ppv, Ppv) annotation (Line(points={{-19.3,19.3},{40,19.3},
                {40,84},{110,84}}, color={0,0,127}));
        connect(storeIsland.Prtu_east, Prtu_east) annotation (Line(points={{-19.3,16.1},
                {52,16.1},{52,54},{110,54}}, color={0,0,127}));
        connect(storeIsland.Prtu_west, Prtu_west) annotation (Line(points={{-19.3,17.7},
                {44,17.7},{44,68},{110,68}}, color={0,0,127}));
        connect(storeIsland.Pref, Pref) annotation (Line(points={{-19.3,14.5},{58,14.5},
                {58,40},{110,40}}, color={0,0,127}));
        connect(storeIsland.Pfre, Pfre) annotation (Line(points={{-19.3,12.9},{62,12.9},
                {62,28},{110,28}}, color={0,0,127}));
        connect(storeIsland.Grtu_west, Grtu_west) annotation (Line(points={{-19.3,11.5},
                {98,11.5},{98,12},{110,12}}, color={0,0,127}));
        connect(storeIsland.Grtu_east, Grtu_east) annotation (Line(points={{-19.3,9.9},
                {4,9.9},{4,-4},{110,-4}}, color={0,0,127}));
        connect(storeIsland.Pnet, Pnet) annotation (Line(points={{-19.3,8.3},{0,8.3},{
                0,-20},{110,-20}}, color={0,0,127}));
        connect(uHeat, storeIsland.uHeat) annotation (Line(points={{-120,-10},{
                -80,-10},{-80,10},{-41,10}},
                                    color={0,0,127}));
        connect(J, Pnet) annotation (Line(points={{110,-46},{6,-46},{6,-20},{
                110,-20}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}), Diagram(coordinateSystem(
                preserveAspectRatio=false, extent={{-100,-120},{100,100}})));
      end StoreIsland;
    end Optimization;

    package BaseClasses
      partial model Whole_partial
        parameter Modelica.SIunits.Temperature Trtu_west_0 = 21+273.15 "Initial temperature of rtu west zone";
        parameter Modelica.SIunits.Temperature Trtu_east_0 = 21+273.15 "Initial temperature of rtu east zone";
        parameter Modelica.SIunits.Temperature Tref_0 = 3.5+273.15 "Initial temperature of ref zone";
        parameter Modelica.SIunits.Temperature Tfre_0 = -25+273.15 "Initial temperature of fre zone";
        parameter Modelica.SIunits.DimensionlessRatio SOC_0 = 0.5 "Initial SOC of battery";
        Thermal thermal(
          Trtu_west_0=Trtu_west_0,
          Trtu_east_0=Trtu_east_0,
          Tref_0=Tref_0,
          Tfre_0=Tfre_0,
          RefCoolingCOP=1.3,
          FreCoolingCOP=1.7)
        annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
        PV.Simple pv(A=5)
          annotation (Placement(transformation(extent={{-40,70},{-20,90}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet
          annotation (Placement(transformation(extent={{100,-70},{120,-50}}),
              iconTransformation(extent={{100,-88},{120,-68}})));
        Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
          annotation (Placement(transformation(extent={{100,-130},{120,-110}}),
              iconTransformation(extent={{100,-148},{120,-128}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west
          "Rtu zone air temperature" annotation (Placement(transformation(
                extent={{100,-90},{120,-70}}), iconTransformation(extent={{100,
                  -108},{120,-88}})));
        Modelica.Blocks.Math.Gain gainPVGen(k=-1)
          annotation (Placement(transformation(extent={{20,94},{32,106}})));
        Modelica.Blocks.Interfaces.RealOutput Ppv "Power generated by PV system"
          annotation (Placement(transformation(extent={{100,90},{120,110}}),
              iconTransformation(extent={{100,74},{120,94}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_west
          "RTU electrical power consumption" annotation (Placement(
              transformation(extent={{100,70},{120,90}}), iconTransformation(
                extent={{100,54},{120,74}})));
        Modelica.Blocks.Interfaces.RealOutput Pbattery "Battery power "
          annotation (Placement(transformation(extent={{100,-10},{120,10}}),
              iconTransformation(extent={{100,-26},{120,-6}})));
        Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
        annotation (Placement(transformation(extent={{100,-150},{120,-130}}),
              iconTransformation(extent={{100,-168},{120,-148}})));
        Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
        annotation (Placement(transformation(extent={{100,30},{120,50}}),
              iconTransformation(extent={{100,14},{120,34}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
        annotation (Placement(transformation(extent={{100,10},{120,30}}),
              iconTransformation(extent={{100,-6},{120,14}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
        annotation (Placement(transformation(extent={{100,-170},{120,-150}}),
              iconTransformation(extent={{100,-188},{120,-168}})));
        Modelica.Blocks.Math.MultiSum multiSum(nu=6)
        annotation (Placement(transformation(extent={{68,-66},{80,-54}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_west "RTU gas power"
          annotation (Placement(transformation(extent={{100,-30},{120,-10}}),
              iconTransformation(extent={{100,-48},{120,-28}})));
        Batteries.Simple Battery(
          Ecap(displayUnit="kWh") = 626400000,
          P_cap=10900,
          SOC_0=SOC_0)
          annotation (Placement(transformation(extent={{-40,-60},{-20,-40}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_east
          "RTU electrical power consumption" annotation (Placement(
              transformation(extent={{100,50},{120,70}}), iconTransformation(
                extent={{100,34},{120,54}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_east "RTU gas power"
          annotation (Placement(transformation(extent={{100,-50},{120,-30}}),
              iconTransformation(extent={{100,-68},{120,-48}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east
          "Rtu zone air temperature" annotation (Placement(transformation(
                extent={{100,-110},{120,-90}}), iconTransformation(extent={{100,
                  -128},{120,-108}})));
      equation
        connect(thermal.Trtu_west, Trtu_west) annotation (Line(points={{-19.3,
                19.3},{10,19.3},{10,-80},{110,-80}}, color={0,0,127}));
        connect(pv.Pgen, gainPVGen.u) annotation (Line(points={{-18.8,80},{-10,
                80},{-10,100},{18.8,100}},                 color={0,0,127}));
        connect(gainPVGen.y, Ppv) annotation (Line(points={{32.6,100},{110,100}},
                                 color={0,0,127}));
        connect(thermal.Prtu_west, Prtu_west) annotation (Line(points={{-19.3,
                17.1},{-4,17.1},{-4,80},{110,80}}, color={0,0,127}));
        connect(thermal.Tref, Tref) annotation (Line(points={{-19.3,6.5},{8,6.5},
                {8,-140},{110,-140}},            color={0,0,127}));
        connect(thermal.Pref, Pref) annotation (Line(points={{-19.3,4.5},{0,4.5},
                {0,40},{110,40}},            color={0,0,127}));
        connect(thermal.Pfre, Pfre) annotation (Line(points={{-19.3,0.7},{4,0.7},
                {4,20},{110,20}},
                         color={0,0,127}));
        connect(thermal.Tfre, Tfre) annotation (Line(points={{-19.3,2.5},{6,2.5},
                {6,-160},{110,-160}},            color={0,0,127}));
        connect(multiSum.u[1], Prtu_west) annotation (Line(points={{68,-56.5},{
                44,-56.5},{44,80},{110,80}}, color={0,0,127}));
        connect(multiSum.u[2], Pref) annotation (Line(points={{68,-57.9},{58,
                -57.9},{58,-58},{48,-58},{48,40},{110,40}},
                                color={0,0,127}));
        connect(multiSum.u[3], Pfre) annotation (Line(points={{68,-59.3},{62,
                -59.3},{62,-58},{50,-58},{50,20},{110,20}},
                                                 color={0,0,127}));
        connect(multiSum.u[4], Pbattery) annotation (Line(points={{68,-60.7},{
                52,-60.7},{52,0},{110,0}},
                                        color={0,0,127}));
        connect(gainPVGen.y, multiSum.u[5]) annotation (Line(points={{32.6,100},
                {42,100},{42,-62.1},{68,-62.1}}, color={0,0,127}));
        connect(thermal.Grtu_west, Grtu_west) annotation (Line(points={{-19.3,
                15.3},{40,15.3},{40,-20},{110,-20}}, color={0,0,127}));
        connect(Battery.SOC, SOC) annotation (Line(points={{-18.8,-46},{-5.4,
                -46},{-5.4,-120},{110,-120}},
                                         color={0,0,127}));
        connect(Battery.Preal, Pbattery) annotation (Line(points={{-18.8,-54},{
                20,-54},{20,0},{110,0}},   color={0,0,127}));
        connect(thermal.Trtu_east, Trtu_east) annotation (Line(points={{-19.3,
                11.9},{30,11.9},{30,-100},{110,-100}}, color={0,0,127}));
        connect(thermal.Prtu_east, Prtu_east) annotation (Line(points={{-19.3,
                10.1},{-2,10.1},{-2,60},{110,60}}, color={0,0,127}));
        connect(thermal.Grtu_east, Grtu_east) annotation (Line(points={{-19.3,
                8.3},{16,8.3},{16,-40},{110,-40}}, color={0,0,127}));
        connect(thermal.Prtu_east, multiSum.u[6]) annotation (Line(points={{-19.3,
                10.1},{-2,10.1},{-2,60},{46,60},{46,-66},{64,-66},{64,-63.5},{
                68,-63.5}},             color={0,0,127}));
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
        parameter Modelica.SIunits.HeatCapacity Crtu_west=1e6 "Heat capacity of RTU west zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.HeatCapacity Crtu_east=1e6 "Heat capacity of RTU east zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rrtu_west=0.0010 "Thermal resistance of west RTU zone to outside" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rrtu_east=0.0010 "Thermal resistance of east RTU zone to outside" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rwest_east=0.0010 "Thermal resistance of east-west RTU zones" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUWestHeatingCap = 29300 "Heating capacity of west RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUEastHeatingCap = 29300 "Heating capacity of east RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUWestCoolingCap = 16998 "Cooling capacity of west RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUEastCoolingCap = 16998 "Cooling capacity of east RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUWestHeatingEff = 0.8 "Heating efficiency of west RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUEastHeatingEff = 0.8 "Heating efficiency of east RTU" annotation(Dialog(group = "RTU"));
        parameter Real RTUWestCoolingCOP = 3 "Cooling COP of west RTU" annotation(Dialog(group = "RTU"));
        parameter Real RTUEastCoolingCOP = 3 "Cooling COP of east RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Temperature Trtu_west_0 = 21+273.15 "Initial temperature of west RTU zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Temperature Trtu_east_0 = 21+273.15 "Initial temperature of east RTU zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.HeatCapacity Cref=1e6 "Heat capacity of refrigerator zone" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.ThermalResistance Rref=0.007 "Thermal resistance of refrigerator zone to RTU west zone" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.Power RefCoolingCap = 6096 "Cooling capacity of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Real RefCoolingCOP = 3 "Cooling COP of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.Temperature Tref_0 = 3.5+273.15 "Initial temperature of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.HeatCapacity Cfre=1e6 "Heat capacity of freezer zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.ThermalResistance Rfre=0.005 "Thermal resistance of freezer zone to RTU east zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreCoolingCap = 5861 "Cooling capacity of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreHeatingCap = 3500 "Defrost heating capacity of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreHeatingEff = 0.99 "Heating efficiency of freezer" annotation(Dialog(group = "Freezer"));
        parameter Real FreCoolingCOP = 3 "Cooling COP of frezzer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Temperature Tfre_0 = -25+273.15 "Initial temperature of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.ThermalResistance Rref_fre=0.001 "Thermal resistance of refrigerator zone to freezer zone" annotation(Dialog(group = "Refrigerator"));

        Envelope.R1C1 rtuZone_west(
          Tzone_0=Trtu_west_0,
          C=Crtu_west,
          R=Rrtu_west) "RTU zone on the west side where the staff is located"
          annotation (Placement(transformation(extent={{-20,160},{0,180}})));
        HVACR.SimpleHeaterCooler RTU_west(
          heatingCap=RTUWestHeatingCap,
          coolingCap=RTUWestCoolingCap,
          coolingCOP=RTUWestCoolingCOP,
          heatingEff=RTUWestHeatingEff)
          "RTU system on the west side where the staff is located"
          annotation (Placement(transformation(extent={{-140,130},{-120,150}})));
        Modelica.Blocks.Interfaces.RealInput Tout "Outdoor air temperature"
        annotation (Placement(transformation(extent={{-228,166},{-200,194}}),
              iconTransformation(extent={{-114,92},{-100,106}})));
        Modelica.Blocks.Interfaces.RealInput uCoolWest
          "Cooling signal input for RTU on the west side" annotation (Placement(
              transformation(extent={{-228,26},{-200,54}}), iconTransformation(extent={{-114,22},
                  {-100,36}})));
        Modelica.Blocks.Interfaces.RealInput uHeatWest
          "Heating signal input for the west RTU " annotation (Placement(
              transformation(extent={{-228,66},{-200,94}}), iconTransformation(extent={{-114,46},
                  {-100,60}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west(unit="K")
          "West zone air temperature" annotation (Placement(transformation(
                extent={{200,190},{220,210}}), iconTransformation(extent={{100,
                  86},{114,100}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_west(unit="W")
          "West RTU electric power" annotation (Placement(transformation(extent=
                 {{200,150},{220,170}}), iconTransformation(extent={{100,64},{
                  114,78}})));
        Envelope.R1C1 refZone(
          C=Cref,
          R=Rref,
          Tzone_0=Tref_0)
          annotation (Placement(transformation(extent={{-20,-80},{0,-60}})));
        Modelica.Blocks.Interfaces.RealOutput Tref(unit="K") "Refrigerator air temperature"
          annotation (Placement(transformation(extent={{200,-90},{220,-70}}),
              iconTransformation(extent={{100,-42},{114,-28}})));
        HVACR.SimpleHeaterCooler refCooler(
        heatingCap=0,
        coolingCap=RefCoolingCap,
        coolingCOP=RefCoolingCOP)
        annotation (Placement(transformation(extent={{-140,-122},{-120,-102}})));
        Modelica.Blocks.Interfaces.RealOutput Pref(unit="W") "Refrigerator power"
          annotation (Placement(transformation(extent={{200,-130},{220,-110}}),
              iconTransformation(extent={{100,-62},{114,-48}})));
        Modelica.Blocks.Math.Add addRef
          annotation (Placement(transformation(extent={{100,-120},{120,-100}})));
        Modelica.Blocks.Sources.Constant uRefHeat(k=0)
          annotation (Placement(transformation(extent={{-180,-110},{-160,-90}})));
        Modelica.Blocks.Interfaces.RealInput uRef
          "Cooling signal input for refrigerator"
          annotation (Placement(transformation(extent={{-228,-114},{-200,-86}}),
              iconTransformation(extent={{-114,-56},{-100,-42}})));
        Envelope.R1C1 freZone(Tzone_0=Tfre_0,
          C=Cfre,
          R=Rfre)
          annotation (Placement(transformation(extent={{-20,-160},{0,-140}})));
        Modelica.Blocks.Math.Add addFre
          annotation (Placement(transformation(extent={{100,-180},{120,-160}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre(unit="W") "Freezer power"
          annotation (Placement(transformation(extent={{200,-210},{220,-190}}),
              iconTransformation(extent={{100,-100},{114,-86}})));
        HVACR.SimpleHeaterCooler freCooler(
        coolingCap=FreCoolingCap,
        heatingCap=FreHeatingCap,
        heatingEff=FreHeatingEff,
        coolingCOP=FreCoolingCOP)
        annotation (Placement(transformation(extent={{-140,-180},{-120,-160}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
          "Cooling signal input for freezer"
          annotation (Placement(transformation(extent={{-228,-194},{-200,-166}}),
              iconTransformation(extent={{-114,-106},{-100,-92}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Defrost signal input for freezer"
          annotation (Placement(transformation(extent={{-228,-154},{-200,-126}}),
              iconTransformation(extent={{-114,-80},{-100,-66}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre(unit="K") "Freezer air temperature"
          annotation (Placement(transformation(extent={{200,-170},{220,-150}}),
              iconTransformation(extent={{100,-82},{114,-68}})));
        Buildings.HeatTransfer.Sources.PrescribedTemperature preTout
        annotation (Placement(transformation(extent={{-140,170},{-120,190}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTrtu_west
          annotation (Placement(transformation(extent={{140,160},{160,180}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTref
        annotation (Placement(transformation(extent={{140,-80},{160,-60}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTfre
        annotation (Placement(transformation(extent={{142,-160},{162,-140}})));
        Modelica.Blocks.Sources.Constant gamingHeat(k=25000)
          annotation (Placement(transformation(extent={{-160,50},{-140,70}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_west "West RTU gas power"
          annotation (Placement(transformation(extent={{200,110},{220,130}}),
              iconTransformation(extent={{100,46},{114,60}})));
        Modelica.Blocks.Interfaces.RealOutput Pload(
                                                   unit="W")
          "Power consumption of internal loads"
          annotation (Placement(transformation(extent={{200,70},{220,90}}),
              iconTransformation(extent={{100,30},{114,44}})));
        Modelica.Blocks.Interfaces.RealInput poaWin "Solar radiation on the windows"
          annotation (Placement(transformation(extent={{-228,126},{-200,154}}),
              iconTransformation(extent={{-114,70},{-100,84}})));
        Modelica.Blocks.Math.Add3 heatWest
          annotation (Placement(transformation(extent={{-60,100},{-40,120}})));
        Modelica.Blocks.Math.Gain gain_west(k=33*0.5)
          "Solar heat gain through windows"
          annotation (Placement(transformation(extent={{-160,100},{-140,120}})));
        Modelica.Thermal.HeatTransfer.Components.ThermalResistor resAdj(R=Rref_fre)
          annotation (Placement(transformation(extent={{40,-98},{60,-78}})));
        HVACR.SimpleHeaterCooler RTU_east(
          heatingCap=RTUEastHeatingCap,
          heatingEff=RTUEastHeatingEff,
          coolingCap=RTUEastCoolingCap,
          coolingCOP=RTUEastCoolingCOP)
          "RTU system on the east side where most slot machines are located"
          annotation (Placement(transformation(extent={{-140,-60},{-120,-40}})));
        Envelope.R1C1 rtuZone_east(
          Tzone_0=Trtu_east_0,
          C=Crtu_east,
          R=Rrtu_east) "RTU zone on the east side where the staff is located"
          annotation (Placement(transformation(extent={{-20,20},{0,40}})));
        Modelica.Blocks.Math.Gain gain_east(k=33*0.5)
          "Solar heat gain through windows"
          annotation (Placement(transformation(extent={{-160,-10},{-140,10}})));
        Modelica.Blocks.Math.Add3 heatEast
          annotation (Placement(transformation(extent={{-60,-20},{-40,0}})));
        Modelica.Blocks.Math.Gain IntHeaGaiWest(k=0.45)
          "Internal heat gains on the west side"
          annotation (Placement(transformation(extent={{-120,80},{-100,100}})));
        Modelica.Blocks.Math.Gain IntHeaGaiEast(k=0.55)
          "Internal heat gains on the east side"
          annotation (Placement(transformation(extent={{-120,20},{-100,40}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east(unit="K")
          "East zone air temperature" annotation (Placement(transformation(
                extent={{200,30},{220,50}}), iconTransformation(extent={{100,12},
                  {114,26}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_east(unit="W")
          "East RTU electric power" annotation (Placement(transformation(extent=
                 {{200,-10},{220,10}}), iconTransformation(extent={{100,-6},{
                  114,8}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_east "East RTU gas power"
          annotation (Placement(transformation(extent={{200,-50},{220,-30}}),
              iconTransformation(extent={{100,-24},{114,-10}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTrtu_east
          annotation (Placement(transformation(extent={{140,20},{160,40}})));
        Modelica.Thermal.HeatTransfer.Components.ThermalResistor resAdjWesEas(R=
              Rwest_east)
          annotation (Placement(transformation(extent={{60,90},{80,110}})));
        Modelica.Blocks.Interfaces.RealInput uHeatEast
          "Heating signal input for the east RTU " annotation (Placement(
              transformation(extent={{-228,-14},{-200,14}}), iconTransformation(
                extent={{-114,-2},{-100,12}})));
        Modelica.Blocks.Interfaces.RealInput uCoolEast
          "Cooling signal input for RTU on the east side" annotation (Placement(
              transformation(extent={{-228,-54},{-200,-26}}),
              iconTransformation(extent={{-114,-26},{-100,-12}})));
        Modelica.Blocks.Math.Gain gaiHeaToPow(k=1.0)
          "Considering 80% of power is transmited to heat"
          annotation (Placement(transformation(extent={{-20,60},{0,80}})));
      equation
        connect(RTU_west.qCool, rtuZone_west.qCool) annotation (Line(points={{-119,
                136},{-60,136},{-60,162},{-22,162}}, color={0,0,127}));
        connect(RTU_west.uCool, uCoolWest) annotation (Line(points={{-142,132},{-188,132},
                {-188,40},{-214,40}}, color={0,0,127}));
        connect(RTU_west.uHeat, uHeatWest) annotation (Line(points={{-142,148},{-192,148},
                {-192,80},{-214,80}}, color={0,0,127}));
        connect(refCooler.qCool, refZone.qCool) annotation (Line(points={{-119,-116},{
                -48,-116},{-48,-78},{-22,-78}},
                                  color={0,0,127}));
        connect(addRef.y, Pref)
          annotation (Line(points={{121,-110},{166,-110},{166,-120},{210,-120}},
                                                    color={0,0,127}));
        connect(refCooler.PCool, addRef.u2) annotation (Line(points={{-119,-120},{24,-120},
                {24,-116},{98,-116}},
                                 color={0,0,127}));
        connect(refCooler.PHeat, addRef.u1)
          annotation (Line(points={{-119,-110},{26,-110},{26,-104},{98,-104}},
                                                                   color={0,0,127}));
        connect(refCooler.qHeat, refZone.qHeat)
          annotation (Line(points={{-119,-106},{-56,-106},{-56,-74},{-22,-74}},
                                                     color={0,0,127}));
        connect(uRefHeat.y, refCooler.uHeat) annotation (Line(points={{-159,-100},{-146,
                -100},{-146,-104},{-142,-104}},
                                    color={0,0,127}));
        connect(refCooler.uCool, uRef) annotation (Line(points={{-142,-120},{-190,-120},
                {-190,-100},{-214,-100}},
                                  color={0,0,127}));
        connect(addFre.y, Pfre)
          annotation (Line(points={{121,-170},{166,-170},{166,-200},{210,-200}},
                                                        color={0,0,127}));
        connect(uFreDef, freCooler.uHeat) annotation (Line(points={{-214,-140},{-160,-140},
                {-160,-162},{-142,-162}},
                                      color={0,0,127}));
        connect(freCooler.uCool, uFreCool) annotation (Line(points={{-142,-178},{-160,
                -178},{-160,-180},{-214,-180}},
                                         color={0,0,127}));
        connect(freCooler.qHeat, freZone.qHeat)
          annotation (Line(points={{-119,-164},{-56,-164},{-56,-154},{-22,-154}},
                                                       color={0,0,127}));
        connect(freCooler.qCool, freZone.qCool) annotation (Line(points={{-119,-174},{
                -48,-174},{-48,-158},{-22,-158}},
                                         color={0,0,127}));
        connect(freCooler.PHeat, addFre.u1) annotation (Line(points={{-119,-168},{26,-168},
                {26,-164},{98,-164}},
                                    color={0,0,127}));
        connect(freCooler.PCool, addFre.u2) annotation (Line(points={{-119,-178},{24,-178},
                {24,-176},{98,-176}},
                                    color={0,0,127}));
      connect(Tout, preTout.T)
        annotation (Line(points={{-214,180},{-142,180}},color={0,0,127}));
        connect(preTout.port, rtuZone_west.port_adj) annotation (Line(points={{
                -120,180},{-94,180},{-94,176},{-20,176}}, color={191,0,0}));
        connect(rtuZone_west.port_cap, senTrtu_west.port)
          annotation (Line(points={{-9.8,170},{140,170}}, color={191,0,0}));
        connect(senTrtu_west.T, Trtu_west) annotation (Line(points={{160,170},{
                186,170},{186,200},{210,200}}, color={0,0,127}));
      connect(refZone.port_cap, senTref.port) annotation (Line(points={{-9.8,
                -70},{140,-70}},        color={191,0,0}));
      connect(senTref.T, Tref)
        annotation (Line(points={{160,-70},{186,-70},{186,-80},{210,-80}},
                                                    color={0,0,127}));
      connect(freZone.port_cap, senTfre.port) annotation (Line(points={{-9.8,
                -150},{142,-150}},              color={191,0,0}));
      connect(senTfre.T, Tfre)
        annotation (Line(points={{162,-150},{186,-150},{186,-160},{210,-160}},
                                                      color={0,0,127}));
        connect(RTU_west.PCool, Prtu_west) annotation (Line(points={{-119,132},
                {180,132},{180,160},{210,160}}, color={0,0,127}));
        connect(RTU_west.PHeat, Grtu_west) annotation (Line(points={{-119,142},
                {46,142},{46,120},{210,120}}, color={0,0,127}));
        connect(RTU_west.qHeat, heatWest.u1) annotation (Line(points={{-119,146},
                {-108,146},{-108,118},{-62,118}}, color={0,0,127}));
        connect(heatWest.y, rtuZone_west.qHeat) annotation (Line(points={{-39,
                110},{-32,110},{-32,166},{-22,166}}, color={0,0,127}));
        connect(poaWin, gain_west.u) annotation (Line(points={{-214,140},{-180,140},{-180,
                110},{-162,110}}, color={0,0,127}));
        connect(gain_west.y, heatWest.u2)
          annotation (Line(points={{-139,110},{-62,110}}, color={0,0,127}));
        connect(refZone.port_cap, resAdj.port_a) annotation (Line(points={{-9.8,-70},{
                16,-70},{16,-88},{40,-88}},
                                          color={191,0,0}));
        connect(resAdj.port_b, freZone.port_cap) annotation (Line(points={{60,-88},{80,
                -88},{80,-150},{-9.8,-150}},
                                           color={191,0,0}));
        connect(poaWin, gain_east.u) annotation (Line(points={{-214,140},{-180,140},{-180,
                0},{-162,0}}, color={0,0,127}));
        connect(RTU_east.qHeat, heatEast.u3) annotation (Line(points={{-119,-44},
                {-90,-44},{-90,-18},{-62,-18}}, color={0,0,127}));
        connect(gamingHeat.y, IntHeaGaiWest.u) annotation (Line(points={{-139,60},
                {-130,60},{-130,90},{-122,90}},
                                          color={0,0,127}));
        connect(IntHeaGaiWest.y, heatWest.u3) annotation (Line(points={{-99,90},
                {-90,90},{-90,102},{-62,102}}, color={0,0,127}));
        connect(gamingHeat.y, IntHeaGaiEast.u) annotation (Line(points={{-139,60},
                {-130,60},{-130,30},{-122,30}},
                                          color={0,0,127}));
        connect(gain_east.y, heatEast.u2) annotation (Line(points={{-139,0},{
                -120,0},{-120,-10},{-62,-10}}, color={0,0,127}));
        connect(IntHeaGaiEast.y, heatEast.u1) annotation (Line(points={{-99,30},
                {-90,30},{-90,-2},{-62,-2}}, color={0,0,127}));
        connect(heatEast.y, rtuZone_east.qHeat) annotation (Line(points={{-39,-10},
                {-32,-10},{-32,26},{-22,26}}, color={0,0,127}));
        connect(RTU_east.qCool, rtuZone_east.qCool) annotation (Line(points={{-119,
                -54},{-28,-54},{-28,22},{-22,22}}, color={0,0,127}));
        connect(rtuZone_east.port_cap, senTrtu_east.port)
          annotation (Line(points={{-9.8,30},{140,30}}, color={191,0,0}));
        connect(senTrtu_east.T, Trtu_east) annotation (Line(points={{160,30},{
                180,30},{180,40},{210,40}}, color={0,0,127}));
        connect(RTU_east.PCool, Prtu_east) annotation (Line(points={{-119,-58},{-76,-58},
                {-76,-30},{38,-30},{38,0},{210,0}},           color={0,0,127}));
        connect(RTU_east.PHeat, Grtu_east) annotation (Line(points={{-119,-48},
                {-60,-48},{-60,-40},{210,-40}}, color={0,0,127}));
        connect(preTout.port, rtuZone_east.port_adj) annotation (Line(points={{
                -120,180},{-94,180},{-94,36},{-20,36}}, color={191,0,0}));
        connect(rtuZone_west.port_cap, resAdjWesEas.port_a) annotation (Line(
              points={{-9.8,170},{20,170},{20,100},{60,100}}, color={191,0,0}));
        connect(resAdjWesEas.port_b, senTrtu_east.port) annotation (Line(points=
               {{80,100},{100,100},{100,30},{140,30}}, color={191,0,0}));
        connect(rtuZone_west.port_cap, refZone.port_adj) annotation (Line(
              points={{-9.8,170},{-80,170},{-80,-64},{-20,-64}}, color={191,0,0}));
        connect(rtuZone_east.port_cap, freZone.port_adj) annotation (Line(
              points={{-9.8,30},{-72,30},{-72,-144},{-20,-144}}, color={191,0,0}));
        connect(uHeatEast, RTU_east.uHeat) annotation (Line(points={{-214,
                1.77636e-15},{-186,1.77636e-15},{-186,-42},{-142,-42}}, color={
                0,0,127}));
        connect(uCoolEast, RTU_east.uCool) annotation (Line(points={{-214,-40},
                {-192,-40},{-192,-58},{-142,-58}}, color={0,0,127}));
        connect(gamingHeat.y, gaiHeaToPow.u) annotation (Line(points={{-139,60},
                {-72,60},{-72,70},{-22,70}}, color={0,0,127}));
        connect(gaiHeaToPow.y, Pload) annotation (Line(points={{1,70},{80,70},{
                80,80},{210,80}}, color={0,0,127}));
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
            Rectangle(
              extent={{-72,12},{6,-70}},
              lineColor={0,0,0},
              fillColor={166,166,166},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{6,12},{74,-70}},
              lineColor={0,0,0},
              fillColor={166,166,166},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{20,-50},{36,-60}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              textString="T"),
            Ellipse(
              extent={{20,-48},{36,-64}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{20,-50},{36,-60}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              textString="T"),
            Ellipse(
              extent={{-52,-32},{-36,-48}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-52,-34},{-36,-44}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid,
              textString="T")}),                                     Diagram(
            coordinateSystem(preserveAspectRatio=false, extent={{-200,-200},{200,200}})));
      end Thermal;

      model Supervisory
      Whole_Inputs store
        annotation (Placement(transformation(extent={{-10,28},{10,60}})));
      HVACR.Controllers.SingleStageCoolingController ref_control(deadband=1.5)
        annotation (Placement(transformation(extent={{-60,-6},{-40,14}})));
      HVACR.Controllers.SingleStageCoolingController fre_control(deadband=1.5)
        annotation (Placement(transformation(extent={{-60,-36},{-40,-16}})));
      HVACR.Controllers.TwoStageCoolingController rtu_cool_control
        annotation (Placement(transformation(extent={{-60,24},{-40,44}})));
      HVACR.Controllers.SingleStageHeatingController rtu_heat_control
        annotation (Placement(transformation(extent={{-60,54},{-40,74}})));
      equation
      connect(store.Tref, ref_control.Tmeas) annotation (Line(points={{11,34.2},
                {16,34.2},{16,-10},{-68,-10},{-68,0},{-62,0}},
                                                            color={0,0,127}));
      connect(store.Tfre, fre_control.Tmeas) annotation (Line(points={{11,32.2},
                {18,32.2},{18,-40},{-68,-40},{-68,-30},{-62,-30}},
                                                              color={0,0,127}));
      connect(ref_control.y, store.uRef) annotation (Line(points={{-39,4},{-30,
                4},{-30,35},{-11,35}},
                                     color={0,0,127}));
      connect(fre_control.y, store.uFreCool) annotation (Line(points={{-39,-26},
                {-28,-26},{-28,29},{-11,29}},
                                            color={0,0,127}));
        connect(store.Trtu_west, rtu_cool_control.Tmeas) annotation (Line(
              points={{11,40.2},{14,40.2},{14,22},{-68,22},{-68,30},{-62,30}},
              color={0,0,127}));
        connect(rtu_cool_control.y, store.uCool) annotation (Line(points={{-39,
                34},{-32,34},{-32,47},{-11,47}}, color={0,0,127}));
      connect(rtu_heat_control.Tmeas, rtu_cool_control.Tmeas) annotation (Line(
            points={{-62,60},{-68,60},{-68,50},{-68,50},{-68,30},{-62,30}},
            color={0,0,127}));
        connect(rtu_heat_control.y, store.uHeat) annotation (Line(points={{-39,
                68},{-32,68},{-32,50},{-11,50}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false, extent={{-100,-120},{
                  100,140}})),
        experiment(
          StartTime=7776000,
          StopTime=7948800,
          Interval=300,
          Tolerance=1e-06,
          __Dymola_Algorithm="Cvode"));
      end Supervisory;

      model Refridgeration

        parameter Modelica.SIunits.HeatCapacity Cfre=1e6 "Heat capacity of freezer zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.ThermalResistance Rfre=0.005 "Thermal resistance of freezer zone to RTU east zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.ThermalResistance Rref_fre=0.005 "Thermal resistance of freezer zone to RTU east zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreCoolingCap = 5860 "Cooling capacity of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreHeatingCap = 3500 "Defrost heating capacity of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreHeatingEff = 0.99 "Heating efficiency of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Power FreCoolingCOP = 3 "Cooling COP of frezzer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Temperature Tfre_0=-252.48   "Initial temperature of freezer" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.Temperature Tref_0 = 3.5+273.15 "Initial temperature of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.HeatCapacity Cref=1e6 "Heat capacity of refrigerator zone" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.ThermalResistance Rref=0.007 "Thermal resistance of refrigerator zone to RTU zone" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.Power RefCoolingCap = 6096 "Cooling capacity of refrigerator" annotation(Dialog(group = "Refrigerator"));
        parameter Modelica.SIunits.Power RefCoolingCOP = 3 "Cooling COP of refrigerator" annotation(Dialog(group = "Refrigerator"));
        HVACR.SimpleHeaterCooler freCooler(
          coolingCap=FreCoolingCap,
          heatingCap=FreHeatingCap,
          heatingEff=FreHeatingEff,
          coolingCOP=FreCoolingCOP)
        annotation (Placement(transformation(extent={{-60,-60},{-40,-40}})));
        Envelope.R1C1 freZone(
          Tzone_0=Tfre_0,
          C=Cfre,
          R=Rfre)
          annotation (Placement(transformation(extent={{0,-20},{20,0}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Defrost signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}}),
              iconTransformation(extent={{-120,-50},{-100,-30}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
          "Cooling signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-100},{-100,-60}}),
              iconTransformation(extent={{-120,-80},{-100,-60}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre(unit="K")
          "Freezer air temperature"
          annotation (Placement(transformation(extent={{100,-20},{120,0}}),
              iconTransformation(extent={{100,30},{120,50}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre(unit="W") "Freezer power"
          annotation (Placement(transformation(extent={{100,-70},{120,-50}}),
              iconTransformation(extent={{100,-50},{120,-30}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTref
        annotation (Placement(transformation(extent={{60,-20},{80,0}})));
        Modelica.Blocks.Interfaces.RealInput Trtu_east "East RTU zone temperature"
          annotation (Placement(transformation(extent={{-140,20},{-100,60}}),
              iconTransformation(extent={{-120,30},{-100,50}})));
        Buildings.HeatTransfer.Sources.PrescribedTemperature preTrtu_east
          annotation (Placement(transformation(extent={{-60,0},{-40,20}})));
        Modelica.Thermal.HeatTransfer.Components.ThermalResistor resAdj(R=Rref_fre)
          annotation (Placement(transformation(extent={{30,20},{50,40}})));
        Modelica.Blocks.Interfaces.RealInput Trtu_west "RTU west zone temperature"
          annotation (Placement(transformation(extent={{-140,60},{-100,100}}),
              iconTransformation(extent={{-120,60},{-100,80}})));
        Buildings.HeatTransfer.Sources.PrescribedTemperature preTrtu_west
          annotation (Placement(transformation(extent={{-58,70},{-38,90}})));
        Envelope.R1C1 refZone(
          C=Cref,
          R=Rref,
          Tzone_0=Tref_0)
          annotation (Placement(transformation(extent={{0,70},{20,90}})));
        Modelica.Blocks.Interfaces.RealInput uRef
          "Cooling signal input for refridgerator" annotation (Placement(
              transformation(extent={{-140,-20},{-100,20}}), iconTransformation(
                extent={{-120,-10},{-100,10}})));
        Modelica.Blocks.Sources.Constant uHeat(k=0)
        annotation (Placement(transformation(extent={{-40,30},{-20,50}})));
        Modelica.Blocks.Interfaces.RealOutput Tref(unit="K")
          "Refridgerator air temperature" annotation (Placement(transformation(extent=
                 {{100,70},{120,90}}), iconTransformation(extent={{100,-10},{
                  120,10}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTref1
        annotation (Placement(transformation(extent={{66,70},{86,90}})));
      equation
        connect(freCooler.qHeat, freZone.qHeat)
          annotation (Line(points={{-39,-44},{-20,-44},{-20,-14},{-2,-14}},
                                                                  color={0,0,127}));
        connect(freCooler.qCool, freZone.qCool)
          annotation (Line(points={{-39,-54},{-20,-54},{-20,-18},{-2,-18}},
                                                                  color={0,0,127}));
        connect(uFreDef, freCooler.uHeat) annotation (Line(points={{-120,-40},{-94,-40},
                {-94,-42},{-62,-42}},
                               color={0,0,127}));
        connect(uFreCool, freCooler.uCool) annotation (Line(points={{-120,-80},{-72,-80},
                {-72,-58},{-62,-58}},
                                  color={0,0,127}));
        connect(freZone.port_cap, senTref.port)
          annotation (Line(points={{10.2,-10},{60,-10}},
                                                       color={191,0,0}));
        connect(senTref.T, Tfre) annotation (Line(points={{80,-10},{110,-10}},
                      color={0,0,127}));
        connect(freCooler.PCool, Pfre) annotation (Line(points={{-39,-58},{-12,-58},{-12,
                -60},{110,-60}},
                            color={0,0,127}));
        connect(Trtu_east, preTrtu_east.T) annotation (Line(points={{-120,40},{-92,40},
                {-92,10},{-62,10}}, color={0,0,127}));
        connect(preTrtu_east.port, freZone.port_adj) annotation (Line(points={{-40,10},
                {-20,10},{-20,-4},{0,-4}}, color={191,0,0}));
        connect(freZone.port_cap, resAdj.port_a) annotation (Line(points={{10.2,-10},{
                24,-10},{24,30},{30,30}}, color={191,0,0}));
        connect(Trtu_west, preTrtu_west.T)
          annotation (Line(points={{-120,80},{-60,80}}, color={0,0,127}));
        connect(preTrtu_west.port, refZone.port_adj) annotation (Line(points={{-38,80},
                {-16,80},{-16,86},{0,86}}, color={191,0,0}));
        connect(refZone.port_cap, resAdj.port_b) annotation (Line(points={{10.2,80},{62,
                80},{62,30},{50,30}}, color={191,0,0}));
        connect(uRef, refZone.qCool) annotation (Line(points={{-120,0},{-80,0},{-80,64},
                {-10,64},{-10,72},{-2,72}}, color={0,0,127}));
        connect(uHeat.y, refZone.qHeat) annotation (Line(points={{-19,40},{-14,40},{-14,
                76},{-2,76}}, color={0,0,127}));
        connect(senTref1.port, resAdj.port_b) annotation (Line(points={{66,80},{62,80},
                {62,30},{50,30}}, color={191,0,0}));
        connect(senTref1.T, Tref)
          annotation (Line(points={{86,80},{110,80}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Refridgeration;

      model Rtu
        parameter Modelica.SIunits.HeatCapacity Crtu_west=1e6 "Heat capacity of RTU west zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.HeatCapacity Crtu_east=1e6 "Heat capacity of RTU east zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rrtu_west=0.0010 "Thermal resistance of west RTU zone to outside" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rrtu_east=0.0010 "Thermal resistance of east RTU zone to outside" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rwest_east=0.0010 "Thermal resistance of east-west RTU zones" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUWestHeatingCap = 29300 "Heating capacity of west RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUEastHeatingCap = 29300 "Heating capacity of east RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUWestCoolingCap = 24910 "Cooling capacity of west RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Power RTUEastCoolingCap = 24910 "Cooling capacity of east RTU" annotation(Dialog(group = "RTU"));
        parameter Real RTUWestHeatingEff = 0.8 "Heating efficiency of west RTU" annotation(Dialog(group = "RTU"));
        parameter Real RTUEastHeatingEff = 0.8 "Heating efficiency of east RTU" annotation(Dialog(group = "RTU"));
        parameter Real RTUWestCoolingCOP = 2.59 "Cooling COP of west RTU" annotation(Dialog(group = "RTU"));
        parameter Real RTUEastCoolingCOP = 2.59 "Cooling COP of east RTU" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Temperature Trtu_west_0 = 21+273.15 "Initial temperature of west RTU zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.Temperature Trtu_east_0 = 21+273.15 "Initial temperature of east RTU zone" annotation(Dialog(group = "RTU"));
        parameter Modelica.SIunits.ThermalResistance Rfre=0.005 "Thermal resistance of freezer zone to RTU east zone" annotation(Dialog(group = "Freezer"));
        parameter Modelica.SIunits.ThermalResistance Rref=0.007 "Thermal resistance of refrigerator zone to RTU zone" annotation(Dialog(group = "Refrigerator"));

        Envelope.R1C1 rtuZone_east(
          Tzone_0=Trtu_east_0,
          C=Crtu_east,
          R=Rrtu_east) "RTU zone on the east side where the staff is located"
          annotation (Placement(transformation(extent={{0,-50},{20,-30}})));
        Envelope.R1C1 rtuZone_west(
          Tzone_0=Trtu_west_0,
          C=Crtu_west,
          R=Rrtu_west) "RTU zone on the west side where the staff is located"
          annotation (Placement(transformation(extent={{0,90},{20,110}})));
        Buildings.HeatTransfer.Sources.PrescribedTemperature preTout
        annotation (Placement(transformation(extent={{-120,90},{-100,110}})));
        HVACR.SimpleHeaterCooler RTU_west(
          heatingCap=RTUWestHeatingCap,
          coolingCap=RTUWestCoolingCap,
          coolingCOP=RTUWestCoolingCOP,
          heatingEff=RTUWestHeatingEff)
          "RTU system on the west side where the staff is located"
          annotation (Placement(transformation(extent={{-120,60},{-100,80}})));
        HVACR.SimpleHeaterCooler RTU_east(
          heatingCap=RTUEastHeatingCap,
          heatingEff=RTUEastHeatingEff,
          coolingCap=RTUEastCoolingCap,
          coolingCOP=RTUEastCoolingCOP)
          "RTU system on the east side where most slot machines are located"
          annotation (Placement(transformation(extent={{-120,-130},{-100,-110}})));
        Modelica.Blocks.Math.Add3 heatEast
          annotation (Placement(transformation(extent={{-40,-90},{-20,-70}})));
        Modelica.Blocks.Math.Gain gain_east(k=33*0.5)
          "Solar heat gain through windows"
          annotation (Placement(transformation(extent={{-140,-80},{-120,-60}})));
        Modelica.Blocks.Math.Gain IntHeaGaiEast(k=0.65)
          "Internal heat gains on the east side"
          annotation (Placement(transformation(extent={{-100,-50},{-80,-30}})));
        Modelica.Blocks.Sources.Constant gamingHeat(k=21300)
          annotation (Placement(transformation(extent={{-140,-20},{-120,0}})));
        Modelica.Blocks.Math.Gain IntHeaGaiWest(k=0.35)
          "Internal heat gains on the west side"
          annotation (Placement(transformation(extent={{-100,10},{-80,30}})));
        Modelica.Blocks.Math.Gain gain_west(k=33*0.5)
          "Solar heat gain through windows"
          annotation (Placement(transformation(extent={{-140,30},{-120,50}})));
        Modelica.Blocks.Math.Add3 heatWest
          annotation (Placement(transformation(extent={{-40,30},{-20,50}})));
        Modelica.Thermal.HeatTransfer.Components.ThermalResistor resAdjWesEas(R=
              Rwest_east)
          annotation (Placement(transformation(extent={{46,20},{66,40}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTrtu_east
          annotation (Placement(transformation(extent={{102,-50},{122,-30}})));
        Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor senTrtu_west
          annotation (Placement(transformation(extent={{100,90},{120,110}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east(unit="K")
          "East zone air temperature" annotation (Placement(transformation(
                extent={{160,-50},{180,-30}}),
                                             iconTransformation(extent={{100,-34},{114,
                  -20}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west(unit="K")
          "West zone air temperature" annotation (Placement(transformation(
                extent={{160,98},{180,118}}),  iconTransformation(extent={{100,66},{114,
                  80}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_west(unit="W")
          "West RTU electric power" annotation (Placement(transformation(extent={{160,58},
                  {180,78}}),            iconTransformation(extent={{100,40},{114,54}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_east(unit="W")
          "East RTU electric power" annotation (Placement(transformation(extent={{160,-90},
                  {180,-70}}),          iconTransformation(extent={{100,-60},{114,-46}})));
        Modelica.Blocks.Interfaces.RealInput Tout "Outdoor air temperature"
        annotation (Placement(transformation(extent={{-208,74},{-180,102}}),
              iconTransformation(extent={{-114,54},{-100,68}})));
        Modelica.Blocks.Interfaces.RealInput poaWin "Solar radiation on the windows"
          annotation (Placement(transformation(extent={{-208,34},{-180,62}}),
              iconTransformation(extent={{-114,32},{-100,46}})));
        Modelica.Blocks.Interfaces.RealInput uHeatWest
          "Heating signal input for the west RTU " annotation (Placement(
              transformation(extent={{-208,-26},{-180,2}}), iconTransformation(extent={{-114,8},
                  {-100,22}})));
        Modelica.Blocks.Interfaces.RealInput uCoolWest
          "Cooling signal input for RTU on the west side" annotation (Placement(
              transformation(extent={{-208,-66},{-180,-38}}),
                                                            iconTransformation(extent={{-114,
                  -28},{-100,-14}})));
        Modelica.Blocks.Interfaces.RealInput uHeatEast
          "Heating signal input for the east RTU " annotation (Placement(
              transformation(extent={{-208,-106},{-180,-78}}),
                                                             iconTransformation(
                extent={{-114,-52},{-100,-38}})));
        Modelica.Blocks.Interfaces.RealInput uCoolEast
          "Cooling signal input for RTU on the east side" annotation (Placement(
              transformation(extent={{-208,-146},{-180,-118}}),
              iconTransformation(extent={{-114,-76},{-100,-62}})));
        Modelica.Thermal.HeatTransfer.Components.ThermalResistor resFre(R=Rfre)
          annotation (Placement(transformation(extent={{40,-102},{60,-82}})));
        Modelica.Blocks.Interfaces.RealInput Tfre "Freezer zone air temperature"
          annotation (Placement(transformation(extent={{-208,-174},{-180,-146}}),
              iconTransformation(extent={{-114,-100},{-100,-86}})));
        Buildings.HeatTransfer.Sources.PrescribedTemperature preTout1
        annotation (Placement(transformation(extent={{-120,-160},{-100,-140}})));
        Modelica.Blocks.Interfaces.RealInput Tref
          "Refridgerator zone air temperature" annotation (Placement(transformation(
                extent={{-208,114},{-180,142}}), iconTransformation(extent={{-114,72},
                  {-100,86}})));
        Buildings.HeatTransfer.Sources.PrescribedTemperature preTout2
        annotation (Placement(transformation(extent={{-120,120},{-100,140}})));
        Modelica.Thermal.HeatTransfer.Components.ThermalResistor resRef(R=Rref)
          annotation (Placement(transformation(extent={{40,120},{60,140}})));
      equation
        connect(Tout, preTout.T) annotation (Line(points={{-194,88},{-158,88},{-158,100},
                {-122,100}}, color={0,0,127}));
        connect(preTout.port, rtuZone_west.port_adj) annotation (Line(points={{-100,100},
                {-50,100},{-50,106},{0,106}}, color={191,0,0}));
        connect(rtuZone_west.port_cap, resAdjWesEas.port_a) annotation (Line(points={{
                10.2,100},{30,100},{30,30},{46,30}}, color={191,0,0}));
        connect(rtuZone_west.port_cap, senTrtu_west.port)
          annotation (Line(points={{10.2,100},{100,100}}, color={191,0,0}));
        connect(rtuZone_east.port_cap, senTrtu_east.port)
          annotation (Line(points={{10.2,-40},{102,-40}}, color={191,0,0}));
        connect(poaWin, gain_west.u) annotation (Line(points={{-194,48},{-160,48},{-160,
                40},{-142,40}}, color={0,0,127}));
        connect(uHeatWest, RTU_west.uHeat) annotation (Line(points={{-194,-12},{-168,-12},
                {-168,78},{-122,78}}, color={0,0,127}));
        connect(uCoolWest, RTU_west.uCool) annotation (Line(points={{-194,-52},{-154,-52},
                {-154,62},{-122,62}}, color={0,0,127}));
        connect(uHeatEast, RTU_east.uHeat) annotation (Line(points={{-194,-92},{-164,-92},
                {-164,-112},{-122,-112}}, color={0,0,127}));
        connect(uCoolEast, RTU_east.uCool) annotation (Line(points={{-194,-132},{-158,
                -132},{-158,-128},{-122,-128}}, color={0,0,127}));
        connect(gamingHeat.y, IntHeaGaiWest.u) annotation (Line(points={{-119,-10},{-108,
                -10},{-108,20},{-102,20}}, color={0,0,127}));
        connect(gamingHeat.y, IntHeaGaiEast.u) annotation (Line(points={{-119,-10},{-108,
                -10},{-108,-40},{-102,-40}}, color={0,0,127}));
        connect(poaWin, gain_east.u) annotation (Line(points={{-194,48},{-160,48},{-160,
                -70},{-142,-70}}, color={0,0,127}));
        connect(gain_east.y, heatEast.u3) annotation (Line(points={{-119,-70},{-78,-70},
                {-78,-88},{-42,-88}}, color={0,0,127}));
        connect(IntHeaGaiEast.y, heatEast.u2) annotation (Line(points={{-79,-40},{-60,
                -40},{-60,-80},{-42,-80}}, color={0,0,127}));
        connect(RTU_east.qHeat, heatEast.u1) annotation (Line(points={{-99,-114},{-54,
                -114},{-54,-72},{-42,-72}}, color={0,0,127}));
        connect(heatEast.y, rtuZone_east.qHeat) annotation (Line(points={{-19,-80},{-12,
                -80},{-12,-44},{-2,-44}}, color={0,0,127}));
        connect(RTU_east.qCool, rtuZone_east.qCool) annotation (Line(points={{-99,-124},
                {-8,-124},{-8,-48},{-2,-48}}, color={0,0,127}));
        connect(IntHeaGaiWest.y, heatWest.u3) annotation (Line(points={{-79,20},{-56,20},
                {-56,32},{-42,32}}, color={0,0,127}));
        connect(gain_west.y, heatWest.u2)
          annotation (Line(points={{-119,40},{-42,40}}, color={0,0,127}));
        connect(RTU_west.qHeat, heatWest.u1) annotation (Line(points={{-99,76},{-66,76},
                {-66,48},{-42,48}}, color={0,0,127}));
        connect(heatWest.y, rtuZone_west.qHeat) annotation (Line(points={{-19,40},{-8,
                40},{-8,96},{-2,96}}, color={0,0,127}));
        connect(RTU_west.qCool, rtuZone_west.qCool) annotation (Line(points={{-99,66},
                {-30,66},{-30,92},{-2,92}}, color={0,0,127}));
        connect(senTrtu_west.T, Trtu_west) annotation (Line(points={{120,100},{140,100},
                {140,108},{170,108}}, color={0,0,127}));
        connect(senTrtu_east.T, Trtu_east)
          annotation (Line(points={{122,-40},{170,-40}}, color={0,0,127}));
        connect(resAdjWesEas.port_b, senTrtu_east.port) annotation (Line(points={{66,30},
                {74,30},{74,-40},{102,-40}}, color={191,0,0}));
        connect(preTout.port, rtuZone_east.port_adj) annotation (Line(points={{-100,100},
                {-50,100},{-50,-34},{0,-34}}, color={191,0,0}));
        connect(RTU_west.PCool, Prtu_west) annotation (Line(points={{-99,62},{88,62},{
                88,68},{170,68}}, color={0,0,127}));
        connect(RTU_east.PCool, Prtu_east) annotation (Line(points={{-99,-128},{120,-128},
                {120,-80},{170,-80}}, color={0,0,127}));
        connect(Tfre, preTout1.T) annotation (Line(points={{-194,-160},{-140,-160},{-140,
                -150},{-122,-150}}, color={0,0,127}));
        connect(preTout1.port, resFre.port_a) annotation (Line(points={{-100,-150},{20,
                -150},{20,-92},{40,-92}}, color={191,0,0}));
        connect(rtuZone_east.port_cap, resFre.port_b) annotation (Line(points={{10.2,-40},
                {80,-40},{80,-92},{60,-92}}, color={191,0,0}));
        connect(Tref, preTout2.T) annotation (Line(points={{-194,128},{-160,128},{-160,
                130},{-122,130}}, color={0,0,127}));
        connect(preTout2.port, resRef.port_a) annotation (Line(points={{-100,130},{-10,
                130},{-10,130},{40,130}}, color={191,0,0}));
        connect(resRef.port_b, rtuZone_west.port_cap) annotation (Line(points={{60,130},
                {72,130},{72,100},{10.2,100}}, color={191,0,0}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid)}),                      Diagram(
              coordinateSystem(preserveAspectRatio=false, extent={{-180,-160},{160,140}})));
      end Rtu;

      model Whole_Derivative
        extends Building.BaseClasses.Whole_partial;
        parameter Modelica.SIunits.DimensionlessRatio uHeat_0 = 0.0 "Initial heating signal";
        parameter Modelica.SIunits.DimensionlessRatio uCool_0 = 0.0 "Initial cooling signal";
        parameter Modelica.SIunits.DimensionlessRatio uBattery_0 = 0.0 "Initial battery control signal";
        Modelica.Blocks.Interfaces.RealInput duHeat
          "Derivative of RTU heating signal input" annotation (Placement(
              transformation(extent={{-140,-10},{-100,30}}), iconTransformation(
                extent={{-140,0},{-100,40}})));
        Modelica.Blocks.Continuous.Integrator intHeatWest(initType=Modelica.Blocks.Types.Init.InitialState,
            y_start=uHeat_0)
          annotation (Placement(transformation(extent={{-88,-4},{-80,4}})));
        Modelica.Blocks.Continuous.Integrator intCool(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
            uCool_0)
          annotation (Placement(transformation(extent={{-88,-24},{-80,-16}})));
        Modelica.Blocks.Interfaces.RealInput duCool
          "Derivative of RTU cooling signal input" annotation (Placement(
              transformation(extent={{-140,-40},{-100,0}}), iconTransformation(
                extent={{-140,-40},{-100,0}})));
        Modelica.Blocks.Interfaces.RealInput duBattery
          "Derivative of control signal for battery"
          annotation (Placement(transformation(extent={{-140,-200},{-100,-160}}),
              iconTransformation(extent={{-140,-80},{-100,-40}})));
        Modelica.Blocks.Continuous.Integrator intBattery(initType=Modelica.Blocks.Types.Init.InitialState,
            y_start=uBattery_0)
          annotation (Placement(transformation(extent={{-94,-184},{-86,-176}})));
      Modelica.Blocks.Interfaces.RealOutput uBattery
          "Connector of Real output signal"
          annotation (Placement(transformation(extent={{100,-270},{120,-250}}),
              iconTransformation(extent={{100,-168},{120,-148}})));
      Modelica.Blocks.Interfaces.RealOutput uCoolWest
          "Connector of Real output signal" annotation (Placement(transformation(
                extent={{100,-196},{120,-176}}), iconTransformation(extent={{100,
                  -10},{120,10}})));
      Modelica.Blocks.Interfaces.RealOutput uHeatWest
          "Connector of Real output signal" annotation (Placement(transformation(
                extent={{100,-184},{120,-164}}), iconTransformation(extent={{100,
                  -46},{120,-26}})));
      Modelica.Blocks.Interfaces.RealInput weaTDryBul
          "Outdoor dry bulb temperature" annotation (Placement(transformation(
                extent={{-140,80},{-100,120}}), iconTransformation(extent={{-140,
                  80},{-100,120}})));
      Modelica.Blocks.Interfaces.RealInput weaPoaPv
          "plane of array solar radiation on pv" annotation (Placement(
              transformation(extent={{-140,50},{-100,90}}), iconTransformation(
                extent={{-140,40},{-100,80}})));
      Modelica.Blocks.Interfaces.RealInput weaPoaWin
          "plane of array solar radiation on Windows" annotation (Placement(
              transformation(extent={{-140,20},{-100,60}}),iconTransformation(
                extent={{-140,0},{-100,40}})));
        Modelica.Blocks.Continuous.Integrator intFreCool(initType=Modelica.Blocks.Types.Init.InitialState,
            y_start=uFreCool_0)
          annotation (Placement(transformation(extent={{-88,-114},{-80,-106}})));
        Modelica.Blocks.Continuous.Integrator intRef(initType=Modelica.Blocks.Types.Init.InitialState,
            y_start=uRef_0)
          annotation (Placement(transformation(extent={{-92,-144},{-84,-136}})));
        Modelica.Blocks.Interfaces.RealInput duFreCool
          "Derivative of freezer cooling signal input" annotation (Placement(
              transformation(extent={{-140,-130},{-100,-90}}), iconTransformation(
                extent={{-140,-40},{-100,0}})));
        Modelica.Blocks.Interfaces.RealInput duRef
          "Derivative of refridgerator east cooling signal input" annotation (
            Placement(transformation(extent={{-140,-160},{-100,-120}}),
              iconTransformation(extent={{-140,-40},{-100,0}})));
      Modelica.Blocks.Interfaces.RealOutput uFreCool
          "Connector of Real output signal" annotation (Placement(transformation(
                extent={{100,-240},{120,-220}}), iconTransformation(extent={{100,
                  -46},{120,-26}})));
      Modelica.Blocks.Interfaces.RealOutput uRef
          "Connector of Real output signal" annotation (Placement(transformation(
                extent={{100,-254},{120,-234}}), iconTransformation(extent={{100,
                  -46},{120,-26}})));
      equation
        connect(intHeatWest.y, thermal.uHeatWest) annotation (Line(points={{-79.6,
                0},{-70,0},{-70,15.3},{-40.7,15.3}}, color={0,0,127}));
        connect(thermal.uCoolWest, intCool.y) annotation (Line(points={{-40.7,
                12.9},{-56,12.9},{-56,12},{-66,12},{-66,-20},{-79.6,-20}},
                                                 color={0,0,127}));
        connect(intHeatWest.y, uHeatWest) annotation (Line(points={{-79.6,0},{-70,
                0},{-70,-154},{0,-154},{0,-174},{110,-174}}, color={0,0,127}));
        connect(intCool.y, uCoolWest) annotation (Line(points={{-79.6,-20},{16,
                -20},{16,-186},{110,-186}}, color={0,0,127}));
        connect(intBattery.y, uBattery) annotation (Line(points={{-85.6,-180},{
                -58,-180},{-58,-260},{110,-260}},           color={0,0,127}));
        connect(intBattery.y, Battery.u) annotation (Line(points={{-85.6,-180},{
                -58,-180},{-58,-50},{-42,-50}},
                                             color={0,0,127}));
        connect(duBattery, intBattery.u)
          annotation (Line(points={{-120,-180},{-94.8,-180}}, color={0,0,127}));
        connect(duCool, intCool.u)
          annotation (Line(points={{-120,-20},{-88.8,-20}}, color={0,0,127}));
        connect(weaPoaPv, pv.Iinc) annotation (Line(points={{-120,70},{-60,70},{
                -60,80},{-42,80}}, color={0,0,127}));
        connect(weaTDryBul, thermal.Tout) annotation (Line(points={{-120,100},{
                -70,100},{-70,20},{-40.7,20},{-40.7,19.9}},
                                                          color={0,0,127}));
        connect(weaPoaWin, thermal.poaWin) annotation (Line(points={{-120,40},{
                -80,40},{-80,17.7},{-40.7,17.7}}, color={0,0,127}));
        connect(duHeat, intHeatWest.u) annotation (Line(points={{-120,10},{-94,10},
                {-94,0},{-88.8,0}}, color={0,0,127}));
        connect(duRef, intRef.u)
          annotation (Line(points={{-120,-140},{-92.8,-140}}, color={0,0,127}));
        connect(duFreCool, intFreCool.u)
          annotation (Line(points={{-120,-110},{-88.8,-110}}, color={0,0,127}));
        connect(intRef.y, thermal.uRef) annotation (Line(points={{-83.6,-140},{
                -52,-140},{-52,5.1},{-40.7,5.1}}, color={0,0,127}));
        connect(intFreCool.y, thermal.uFreCool) annotation (Line(points={{-79.6,
                -110},{-46,-110},{-46,0.1},{-40.7,0.1}}, color={0,0,127}));
        connect(intFreCool.y, uFreCool) annotation (Line(points={{-79.6,-110},{
                -76,-110},{-76,-230},{110,-230}}, color={0,0,127}));
        connect(intRef.y, uRef) annotation (Line(points={{-83.6,-140},{-80,-140},
                {-80,-244},{110,-244}}, color={0,0,127}));
        connect(intCool.y, thermal.uCoolEast) annotation (Line(points={{-79.6,-20},
                {-58,-20},{-58,8.1},{-40.7,8.1}}, color={0,0,127}));
        connect(intHeatWest.y, thermal.uHeatEast) annotation (Line(points={{-79.6,
                0},{-62,0},{-62,10.5},{-40.7,10.5}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
            coordinateSystem(preserveAspectRatio=false, extent={{-100,-260},{100,
                  100}})));
      end Whole_Derivative;

      model Whole_Inputs
        extends BaseClasses.Whole_partial(
          pv(
            A=272.6,
            eff=0.26,
            effDcAc=0.98),
          thermal(
            RTUWestHeatingCap=29300,
            RTUEastHeatingCap=29300,
            RTUWestCoolingCap(displayUnit="kW") = 20000,
            RTUEastCoolingCap(displayUnit="kW") = 20000,
            RTUWestCoolingCOP=3,
            RTUEastCoolingCOP=4,
            Rrtu_west=0.0005,
            Rrtu_east=0.0005,
            Rwest_east=0.01,
            Crtu_west=0.5e5,
            Crtu_east=0.5e5,
            Cref=0.5e7,
            Rref=0.1,
            Cfre=0.5e7,
            Rfre=0.1,
            FreHeatingCap=4500,
            FreCoolingCOP=1.15,
            Rref_fre=0.1),
          multiSum(k={1,1,1,1,1,1,1/4,1/4}, nu=8),
          Battery(Ecap=145800000, P_cap=21000));
        parameter Modelica.SIunits.Temperature TSpRtuEast;
        parameter Modelica.SIunits.Temperature TSpRtuWest;
        parameter Modelica.SIunits.Temperature TSpRef;
        parameter Modelica.SIunits.Temperature TSpFre;

        Modelica.Blocks.Interfaces.RealInput uHeat "RTU heating signal input"
          annotation (Placement(transformation(extent={{-140,-10},{-100,30}}),
              iconTransformation(extent={{-120,-10},{-100,10}})));
        Modelica.Blocks.Interfaces.RealInput uCool "RTU cooling signal input"
          annotation (Placement(transformation(extent={{-140,-40},{-100,0}}),
              iconTransformation(extent={{-120,-40},{-100,-20}})));
        Modelica.Blocks.Interfaces.RealInput uBattery "Control signal for battery"
          annotation (Placement(transformation(extent={{-140,-130},{-100,-90}}),
              iconTransformation(extent={{-120,-130},{-100,-110}})));
        Modelica.Blocks.Interfaces.RealInput uRef
        "Cooling signal input for refrigerator"
        annotation (Placement(transformation(extent={{-140,-160},{-100,-120}}),
              iconTransformation(extent={{-120,-160},{-100,-140}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Defrost signal input for freezer"
        annotation (Placement(transformation(extent={{-140,-200},{-100,-160}}),
              iconTransformation(extent={{-120,-190},{-100,-170}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
        "Cooling signal input for freezer"
        annotation (Placement(transformation(extent={{-140,-240},{-100,-200}}),
              iconTransformation(extent={{-120,-220},{-100,-200}})));
        Modelica.Blocks.Math.MultiSum multiSum1(k={1,1,1,1}, nu=4)
          annotation (Placement(transformation(extent={{44,-214},{56,-202}})));
        Modelica.Blocks.Math.Product squareTrtu
        annotation (Placement(transformation(extent={{14,-172},{20,-166}})));
        Buildings.Controls.OBC.CDL.Continuous.Sources.Constant TSetRtuWest(k=
              TSpRtuWest)
          annotation (Placement(transformation(extent={{-80,-170},{-60,-150}})));
        Modelica.Blocks.Math.Add add2(k2=-1)
          annotation (Placement(transformation(extent={{-40,-178},{-20,-158}})));
        Modelica.Blocks.Math.Add add3(k2=-1)
          annotation (Placement(transformation(extent={{-40,-210},{-20,-190}})));
        Modelica.Blocks.Math.Product squareTref
          annotation (Placement(transformation(extent={{14,-204},{20,-198}})));
        Buildings.Controls.OBC.CDL.Continuous.Sources.Constant TSetRef(k=TSpRef)
          annotation (Placement(transformation(extent={{-80,-210},{-60,-190}})));
        Modelica.Blocks.Math.Add add4(k2=-1)
          annotation (Placement(transformation(extent={{-40,-250},{-20,-230}})));
        Modelica.Blocks.Math.Product squareTfre
          annotation (Placement(transformation(extent={{14,-244},{20,-238}})));
        Buildings.Controls.OBC.CDL.Continuous.Sources.Constant TSetFre(k=TSpFre)
          annotation (Placement(transformation(extent={{-80,-250},{-60,-230}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet_pen
          annotation (Placement(transformation(extent={{100,-210},{120,-190}}),
              iconTransformation(extent={{100,-220},{120,-200}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add5
          annotation (Placement(transformation(extent={{70,-210},{90,-190}})));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul
          "Outdoor dry bulb temperature" annotation (Placement(transformation(
                extent={{-140,80},{-100,120}}), iconTransformation(extent={{-120,80},
                  {-100,100}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaPv
          "plane of array solar radiation on pv" annotation (Placement(
              transformation(extent={{-140,50},{-100,90}}), iconTransformation(
                extent={{-120,50},{-100,70}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaWin
          "plane of array solar radiation on Windows" annotation (Placement(
              transformation(extent={{-140,20},{-100,60}}),iconTransformation(
                extent={{-120,20},{-100,40}})));
        Modelica.Blocks.Math.MultiSum multiSum2(nu=7)
        annotation (Placement(transformation(extent={{76,-36},{88,-24}})));
        Modelica.Blocks.Math.Add add1(k2=-1)
          annotation (Placement(transformation(extent={{-40,-130},{-20,-110}})));
        Buildings.Controls.OBC.CDL.Continuous.Sources.Constant TSetRtuEast(k=
              TSpRtuEast)
          annotation (Placement(transformation(extent={{-80,-130},{-60,-110}})));
        Modelica.Blocks.Math.Product squareTrtu1
        annotation (Placement(transformation(extent={{14,-134},{20,-128}})));
        Modelica.Blocks.Math.Gain gainPVGen1(k=1/1000)
          annotation (Placement(transformation(extent={{68,-156},{80,-144}})));
      equation
        connect(thermal.uHeatWest, uHeat) annotation (Line(points={{-40.7,15.3},{
                -82,15.3},{-82,10},{-120,10}}, color={0,0,127}));
        connect(thermal.uCoolWest, uCool) annotation (Line(points={{-40.7,12.9},{
                -94,12.9},{-94,-20},{-120,-20}}, color={0,0,127}));
      connect(thermal.uRef, uRef) annotation (Line(points={{-40.7,5.1},{-92,5.1},
                {-92,-140},{-120,-140}},              color={0,0,127}));
      connect(thermal.uFreDef, uFreDef) annotation (Line(points={{-40.7,2.7},{-90,
                2.7},{-90,-180},{-120,-180}},
                                       color={0,0,127}));
      connect(thermal.uFreCool, uFreCool) annotation (Line(points={{-40.7,0.1},{
                -88,0.1},{-88,-220},{-120,-220}},
                                       color={0,0,127}));
        connect(uBattery, Battery.u) annotation (Line(points={{-120,-110},{-86,
                -110},{-86,-50},{-42,-50}},
                                      color={0,0,127}));
        connect(add2.u1, Trtu_west) annotation (Line(points={{-42,-162},{-48,-162},
                {-48,-80},{110,-80}}, color={0,0,127}));
        connect(add2.y, squareTrtu.u1) annotation (Line(points={{-19,-168},{-4,-168},
                {-4,-167.2},{13.4,-167.2}}, color={0,0,127}));
        connect(TSetRef.y, add3.u2) annotation (Line(points={{-58,-200},{-50,-200},
                {-50,-206},{-42,-206}}, color={0,0,127}));
        connect(add3.y, squareTref.u1) annotation (Line(points={{-19,-200},{-4,-200},
                {-4,-199.2},{13.4,-199.2}}, color={0,0,127}));
        connect(squareTref.u2, add3.y) annotation (Line(points={{13.4,-202.8},{-4.3,
                -202.8},{-4.3,-200},{-19,-200}}, color={0,0,127}));
        connect(add4.y, squareTfre.u1) annotation (Line(points={{-19,-240},{0,-240},{0,
                -239.2},{13.4,-239.2}},    color={0,0,127}));
        connect(TSetFre.y,add4. u2) annotation (Line(points={{-58,-240},{-50,-240},
                {-50,-246},{-42,-246}},  color={0,0,127}));
        connect(squareTfre.u2,add4. y) annotation (Line(points={{13.4,-242.8},{4,-242.8},
                {4,-240},{-19,-240}},         color={0,0,127}));
        connect(add2.y, squareTrtu.u2) annotation (Line(points={{-19,-168},{-4,-168},
                {-4,-170.8},{13.4,-170.8}}, color={0,0,127}));
        connect(multiSum1.y,add5. u2) annotation (Line(points={{57.02,-208},{62,-208},
                {62,-206},{68,-206}},       color={0,0,127}));
        connect(add5.y, Pnet_pen) annotation (Line(points={{92,-200},{110,-200}},
                                      color={0,0,127}));
        connect(TSetRtuWest.y, add2.u2) annotation (Line(points={{-58,-160},{-50,
                -160},{-50,-174},{-42,-174}}, color={0,0,127}));
        connect(add3.u1, Tref) annotation (Line(points={{-42,-194},{-54,-194},{-54,
                -140},{110,-140}}, color={0,0,127}));
        connect(add4.u1, Tfre) annotation (Line(points={{-42,-234},{-52,-234},{-52,-220},
                {-12,-220},{-12,-160},{110,-160}},         color={0,0,127}));
        connect(weaTDryBul, thermal.Tout) annotation (Line(points={{-120,100},{
                -80,100},{-80,19.9},{-40.7,19.9}},
                                               color={0,0,127}));
        connect(weaPoaPv, pv.Iinc) annotation (Line(points={{-120,70},{-68,70},{
                -68,80},{-42,80}}, color={0,0,127}));
        connect(weaPoaWin, thermal.poaWin) annotation (Line(points={{-120,40},{
                -90,40},{-90,17.7},{-40.7,17.7}}, color={0,0,127}));
        connect(gainPVGen.y, multiSum2.u[1]) annotation (Line(points={{32.6,100},{74,100},
                {74,-26.4},{76,-26.4}},          color={0,0,127}));
        connect(multiSum2.u[2], Pref) annotation (Line(points={{76,-27.6},{68,
                -27.6},{68,40},{110,40}}, color={0,0,127}));
        connect(multiSum2.u[3], Pfre) annotation (Line(points={{76,-28.8},{66,
                -28.8},{66,20},{110,20}}, color={0,0,127}));
        connect(multiSum2.u[4], Pbattery) annotation (Line(points={{76,-30},{64,
                -30},{64,0},{110,0}},     color={0,0,127}));
        connect(multiSum2.u[5], Prtu_west) annotation (Line(points={{76,-31.2},{
                72,-31.2},{72,80},{110,80}}, color={0,0,127}));
        connect(thermal.Pload, multiSum2.u[6]) annotation (Line(points={{-19.3,
                13.7},{24,13.7},{24,-32},{50,-32},{50,-32.4},{76,-32.4}},
                                              color={0,0,127}));
        connect(TSetRtuEast.y, add1.u2) annotation (Line(points={{-58,-120},{-54,
                -120},{-54,-126},{-42,-126}}, color={0,0,127}));
        connect(add1.u1, Trtu_east) annotation (Line(points={{-42,-114},{-54,-114},
                {-54,-100},{110,-100}}, color={0,0,127}));
        connect(add1.y, squareTrtu1.u1) annotation (Line(points={{-19,-120},{-10,
                -120},{-10,-129.2},{13.4,-129.2}}, color={0,0,127}));
        connect(add1.y, squareTrtu1.u2) annotation (Line(points={{-19,-120},{-10,
                -120},{-10,-132.8},{13.4,-132.8}}, color={0,0,127}));
        connect(multiSum2.u[7], Prtu_east) annotation (Line(points={{76,-33.6},{
                70,-33.6},{70,60},{110,60}}, color={0,0,127}));
        connect(multiSum2.y, Pnet) annotation (Line(points={{89.02,-30},{94,-30},
                {94,-60},{110,-60}}, color={0,0,127}));
        connect(multiSum.u[7], Grtu_west) annotation (Line(points={{68,-60},{58,
                -60},{58,-20},{110,-20}}, color={0,0,127}));
        connect(multiSum.u[8], Grtu_east) annotation (Line(points={{68,-60},{56,
                -60},{56,-40},{110,-40}}, color={0,0,127}));
        connect(multiSum.y, gainPVGen1.u) annotation (Line(points={{81.02,-60},{
                88,-60},{88,-84},{60,-84},{60,-150},{66.8,-150}}, color={0,0,127}));
        connect(gainPVGen1.y, add5.u1) annotation (Line(points={{80.6,-150},{84,
                -150},{84,-172},{62,-172},{62,-194},{68,-194}}, color={0,0,127}));
        connect(squareTrtu1.y, multiSum1.u[1]) annotation (Line(points={{20.3,
                -131},{32,-131},{32,-204.85},{44,-204.85}}, color={0,0,127}));
        connect(squareTrtu.y, multiSum1.u[2]) annotation (Line(points={{20.3,-169},
                {30,-169},{30,-206.95},{44,-206.95}}, color={0,0,127}));
        connect(squareTref.y, multiSum1.u[3]) annotation (Line(points={{20.3,-201},
                {26,-201},{26,-209.05},{44,-209.05}}, color={0,0,127}));
        connect(squareTfre.y, multiSum1.u[4]) annotation (Line(points={{20.3,-241},
                {30,-241},{30,-211.15},{44,-211.15}}, color={0,0,127}));
        connect(uHeat, thermal.uHeatEast) annotation (Line(points={{-120,10},{-80,
                10},{-80,10.5},{-40.7,10.5}}, color={0,0,127}));
        connect(uCool, thermal.uCoolEast) annotation (Line(points={{-120,-20},{-94,
                -20},{-94,8.1},{-40.7,8.1}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                Bitmap(extent={{-90,-110},{92,-4}}, fileName=
                    "modelica://SolarPlus/StoreFigure.png"),
              Text(
                extent={{-250,170},{250,110}},
                textString="%name",
                lineColor={0,0,255})}),                                Diagram(
              coordinateSystem(preserveAspectRatio=false, extent={{-100,-260},{100,100}})));
      end Whole_Inputs;

      model partialStore
        parameter Modelica.SIunits.Temperature Trtu_west_0 = 21+273.15 "Initial temperature of rtu west zone";
        parameter Modelica.SIunits.Temperature Trtu_east_0 = 21+273.15 "Initial temperature of rtu east zone";
        parameter Modelica.SIunits.Temperature Tref_0 = 3.5+273.15 "Initial temperature of ref zone";
        parameter Modelica.SIunits.Temperature Tfre_0 = -25+273.15 "Initial temperature of fre zone";
        parameter Modelica.SIunits.DimensionlessRatio SOC_0 = 0.5 "Initial SOC of battery";
        SolarPlus.Building.BaseClasses.Whole_Inputs store(
          Trtu_west_0=Trtu_west_0,
          Trtu_east_0=Trtu_east_0,
          Tref_0=Tref_0,
          Tfre_0=Tfre_0,
          SOC_0=SOC_0)
          annotation (Placement(transformation(extent={{-10,28},{10,60}})));
          Modelica.Blocks.Interfaces.RealInput weaPoaPv "plane of array solar radiation on pv"
          annotation (Placement(transformation(
                extent={{-160,90},{-120,130}}),iconTransformation(extent={{-160,40},
                  {-120,80}})));
      Modelica.Blocks.Interfaces.RealInput weaPoaWin "plane of array solar radiation on Windows"
          annotation (Placement(
              transformation(extent={{-160,60},{-120,100}}),iconTransformation(extent={{-160,80},
                  {-120,120}})));
      Modelica.Blocks.Interfaces.RealInput uCool "RTU cooling signal input"
          annotation (Placement(transformation(extent={{-160,0},{-120,40}}),
              iconTransformation(extent={{-160,-80},{-120,-40}})));
      Modelica.Blocks.Interfaces.RealInput uBattery
          "Control signal for battery"
        annotation (Placement(transformation(
                extent={{-160,-90},{-120,-50}}),  iconTransformation(extent={{-160,
                  -160},{-120,-120}})));
      Modelica.Blocks.Interfaces.RealInput uRef
          "Cooling signal input for refrigerator"
        annotation (Placement(transformation(extent={{-160,-120},{-120,-80}}),
              iconTransformation(extent={{-160,-200},{-120,-160}})));
      Modelica.Blocks.Interfaces.RealInput uFreCool
        "Cooling signal input for freezer"
        annotation (Placement(transformation(extent={{-160,-200},{-120,-160}}),
              iconTransformation(extent={{-160,-240},{-120,-200}})));
      Modelica.Blocks.Math.Product squareHeat
        annotation (Placement(transformation(extent={{38,-146},{44,-140}})));
      Modelica.Blocks.Math.Product squareCool
        annotation (Placement(transformation(extent={{38,-156},{44,-150}})));
      Modelica.Blocks.Math.Product squareCharge
        annotation (Placement(transformation(extent={{38,-166},{44,-160}})));
      Modelica.Blocks.Math.Gain gainCharge(k=1)
        annotation (Placement(transformation(extent={{50,-166},{56,-160}})));
      Modelica.Blocks.Math.Gain gainCool(k=1)
        annotation (Placement(transformation(extent={{50,-156},{56,-150}})));
      Modelica.Blocks.Math.Gain gainHeat(k=1)
        annotation (Placement(transformation(extent={{50,-146},{56,-140}})));
        Modelica.Blocks.Math.MultiSum sumJ(nu=7)
        annotation (Placement(transformation(extent={{84,-166},{96,-154}})));
      Modelica.Blocks.Math.Gain gainRef(k=1)
          annotation (Placement(transformation(extent={{50,-186},{56,-180}})));
      Modelica.Blocks.Math.Product squareDischarge1
        annotation (Placement(transformation(extent={{38,-186},{44,-180}})));
      Modelica.Blocks.Math.Gain gainDischarge2(k=1)
        annotation (Placement(transformation(extent={{50,-196},{56,-190}})));
      Modelica.Blocks.Math.Product squareDischarge2
        annotation (Placement(transformation(extent={{38,-196},{44,-190}})));
      Modelica.Blocks.Math.Gain gainFreCool(k=1)
          annotation (Placement(transformation(extent={{50,-206},{56,-200}})));
      Modelica.Blocks.Math.Product squareDischarge3
        annotation (Placement(transformation(extent={{38,-206},{44,-200}})));
        Modelica.Blocks.Interfaces.RealOutput J
        "Objective function for optimization"
        annotation (Placement(transformation(extent={{120,-148},{140,-128}}),
              iconTransformation(extent={{120,-170},{140,-150}})));
        Modelica.Blocks.Interfaces.RealOutput Ppv "Power generated by PV system"
          annotation (Placement(transformation(extent={{120,130},{140,150}}),
              iconTransformation(extent={{120,110},{140,130}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_west
          "RTU west electrical power consumption" annotation (Placement(
              transformation(extent={{120,110},{140,130}}),
              iconTransformation(extent={{120,70},{140,90}})));
      Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
        annotation (Placement(transformation(extent={{120,70},{140,90}}),
              iconTransformation(extent={{120,50},{140,70}})));
      Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
        annotation (Placement(transformation(extent={{120,50},{140,70}}),
              iconTransformation(extent={{120,30},{140,50}})));
        Modelica.Blocks.Interfaces.RealOutput Pbattery "Battery power output"
          annotation (Placement(transformation(extent={{120,30},{140,50}}),
              iconTransformation(extent={{120,10},{140,30}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet
          annotation (Placement(transformation(extent={{120,-30},{140,-10}}),
              iconTransformation(extent={{120,-50},{140,-30}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west
          "Rtu west zone air temperature" annotation (Placement(
              transformation(extent={{120,-50},{140,-30}}),
              iconTransformation(extent={{120,-70},{140,-50}})));
        Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
          annotation (Placement(transformation(extent={{120,-88},{140,-68}}),
              iconTransformation(extent={{120,-110},{140,-90}})));
      Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
        annotation (Placement(transformation(extent={{120,-108},{140,-88}}),
              iconTransformation(extent={{120,-130},{140,-110}})));
      Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
        annotation (Placement(transformation(extent={{120,-128},{140,-108}}),
              iconTransformation(extent={{120,-150},{140,-130}})));
      Modelica.Blocks.Interfaces.RealInput weaTDryBul "Outdoor dry bulb temperature"
          annotation (Placement(transformation(extent={{-160,120},{-120,160}}),
              iconTransformation(extent={{-160,120},{-120,160}})));

        Modelica.Blocks.Interfaces.RealOutput Prtu_east
          "RTU east electrical power consumption" annotation (Placement(
              transformation(extent={{120,90},{140,110}}), iconTransformation(
                extent={{120,90},{140,110}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east
          "Rtu east zone air temperature" annotation (Placement(
              transformation(extent={{120,-70},{140,-50}}),
              iconTransformation(extent={{120,-90},{140,-70}})));
      equation
        connect(store.uCool, uCool) annotation (Line(points={{-11,47},{-100,
                47},{-100,20},{-140,20}}, color={0,0,127}));
        connect(uBattery, store.uBattery) annotation (Line(points={{-140,-70},
                {-96,-70},{-96,38},{-11,38}},
                                            color={0,0,127}));
        connect(uRef, store.uRef) annotation (Line(points={{-140,-100},{-84,
                -100},{-84,35},{-11,35}}, color={0,0,127}));
        connect(store.uFreCool, uFreCool) annotation (Line(points={{-11,29},{
                -80,29},{-80,-180},{-140,-180}},  color={0,0,127}));
      connect(squareCharge.y,gainCharge. u)
        annotation (Line(points={{44.3,-163},{49.4,-163}},
                                                         color={0,0,127}));
      connect(squareCool.y,gainCool. u)
        annotation (Line(points={{44.3,-153},{49.4,-153}},
                                                         color={0,0,127}));
      connect(squareHeat.y,gainHeat. u)
        annotation (Line(points={{44.3,-143},{49.4,-143}},
                                                         color={0,0,127}));
      connect(gainHeat.y,sumJ. u[1]) annotation (Line(points={{56.3,-143},{62,
                -143},{62,-156},{84,-156},{84,-156.4}},
                                        color={0,0,127}));
      connect(gainCool.y,sumJ. u[2]) annotation (Line(points={{56.3,-153},{58,
                -153},{58,-154},{60,-154},{60,-157.6},{84,-157.6}},
                                  color={0,0,127}));
      connect(gainCharge.y,sumJ. u[3]) annotation (Line(points={{56.3,-163},{
                58,-163},{58,-158.8},{84,-158.8}},
                                             color={0,0,127}));
      connect(squareHeat.u2,squareHeat. u1) annotation (Line(points={{37.4,
                -144.8},{16,-144.8},{16,-141.2},{37.4,-141.2}},
                                                   color={0,0,127}));
        connect(uCool, squareCool.u1) annotation (Line(points={{-140,20},{-116,
                20},{-116,-151.2},{37.4,-151.2}}, color={0,0,127}));
      connect(squareCool.u2,squareCool. u1) annotation (Line(points={{37.4,
                -154.8},{16,-154.8},{16,-151.2},{37.4,-151.2}},
                                                   color={0,0,127}));
        connect(uBattery, squareCharge.u1) annotation (Line(points={{-140,-70},
                {-100,-70},{-100,-161.2},{37.4,-161.2}},
              color={0,0,127}));
      connect(squareCharge.u2,squareCharge. u1) annotation (Line(points={{37.4,
                -164.8},{16,-164.8},{16,-161.2},{37.4,-161.2}},
                                                          color={0,0,127}));
        connect(squareDischarge1.y,gainRef. u)
          annotation (Line(points={{44.3,-183},{49.4,-183}}, color={0,0,127}));
      connect(squareDischarge2.y,gainDischarge2. u)
        annotation (Line(points={{44.3,-193},{49.4,-193}},
                                                         color={0,0,127}));
        connect(squareDischarge3.y,gainFreCool. u)
          annotation (Line(points={{44.3,-203},{49.4,-203}}, color={0,0,127}));
        connect(gainRef.y,sumJ. u[4]) annotation (Line(points={{56.3,-183},{
                58,-183},{58,-174},{60,-174},{60,-160},{84,-160}},
              color={0,0,127}));
      connect(gainDischarge2.y,sumJ. u[5]) annotation (Line(points={{56.3,
                -193},{58,-193},{58,-184},{62,-184},{62,-161.2},{84,-161.2}},
                                                  color={0,0,127}));
        connect(gainFreCool.y,sumJ. u[6]) annotation (Line(points={{56.3,-203},
                {60,-203},{60,-194},{64,-194},{64,-162.4},{84,-162.4}},    color=
                {0,0,127}));
      connect(uRef,squareDischarge1. u1) annotation (Line(points={{-140,-100},
                {-106,-100},{-106,-172},{-34,-172},{-34,-181.2},{37.4,-181.2}},
                                                                         color={0,
              0,127}));
      connect(squareDischarge1.u2,squareDischarge1. u1) annotation (Line(points={{37.4,
                -184.8},{16,-184.8},{16,-181.2},{37.4,-181.2}}, color={0,0,127}));
      connect(squareDischarge2.u2,squareDischarge2. u1) annotation (Line(points={{37.4,
                -194.8},{16,-194.8},{16,-191.2},{37.4,-191.2}},   color={0,0,127}));
      connect(uFreCool,squareDischarge3. u1) annotation (Line(points={{-140,
                -180},{-84,-180},{-84,-200},{8,-200},{8,-201.2},{37.4,-201.2}},
                                                  color={0,0,127}));
      connect(squareDischarge3.u2,squareDischarge3. u1) annotation (Line(points={{37.4,
                -204.8},{16,-204.8},{16,-201.2},{37.4,-201.2}},     color={0,0,
              127}));
        connect(Ppv, store.Ppv) annotation (Line(points={{130,140},{40,140},{
                40,58.4},{11,58.4}},
                              color={0,0,127}));
        connect(store.Prtu_west, Prtu_west) annotation (Line(points={{11,56.4},
                {44,56.4},{44,120},{130,120}}, color={0,0,127}));
        connect(Pref, store.Pref) annotation (Line(points={{130,80},{52,80},{
                52,52.4},{11,52.4}},
                              color={0,0,127}));
        connect(Pfre, store.Pfre) annotation (Line(points={{130,60},{54,60},{
                54,50.4},{11,50.4}},
                              color={0,0,127}));
        connect(Pbattery, store.Pbattery) annotation (Line(points={{130,40},{
                56,40},{56,48.4},{11,48.4}},
                                         color={0,0,127}));
        connect(store.Pnet, Pnet) annotation (Line(points={{11,42.2},{52,42.2},
                {52,-20},{130,-20}},
                                 color={0,0,127}));
        connect(store.Trtu_west, Trtu_west) annotation (Line(points={{11,40.2},
                {48,40.2},{48,-40},{130,-40}}, color={0,0,127}));
        connect(SOC, store.SOC) annotation (Line(points={{130,-78},{44,-78},{
                44,36.2},{11,36.2}},
                               color={0,0,127}));
        connect(Tref, store.Tref) annotation (Line(points={{130,-98},{40,-98},
                {40,34.2},{11,34.2}},
                                  color={0,0,127}));
        connect(Tfre, store.Tfre) annotation (Line(points={{130,-118},{100,
                -118},{100,-110},{36,-110},{36,32.2},{11,32.2}},
                                  color={0,0,127}));
        connect(weaTDryBul, store.weaTDryBul) annotation (Line(points={{-140,
                140},{-100,140},{-100,59},{-11,59}},
                                                   color={0,0,127}));
        connect(weaPoaPv, store.weaPoaPv) annotation (Line(points={{-140,110},
                {-106,110},{-106,56},{-11,56}},
                                             color={0,0,127}));
        connect(weaPoaWin, store.weaPoaWin) annotation (Line(points={{-140,80},
                {-110,80},{-110,53},{-11,53}},
                                             color={0,0,127}));
        connect(store.Prtu_east, Prtu_east) annotation (Line(points={{11,54.4},
                {48,54.4},{48,100},{130,100}}, color={0,0,127}));
        connect(store.Trtu_east, Trtu_east) annotation (Line(points={{11,38.2},
                {46,38.2},{46,-60},{130,-60}}, color={0,0,127}));
        connect(store.Pnet_pen, sumJ.u[7]) annotation (Line(points={{11,29},{
                28,29},{28,-114},{76,-114},{76,-159.475},{84,-159.475},{84,
                -163.6}},   color={0,0,127}));
        connect(sumJ.y, J) annotation (Line(points={{97.02,-160},{108,-160},{
                108,-138},{130,-138}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-120,
                  -220},{120,140}})),      Diagram(coordinateSystem(
                preserveAspectRatio=false, extent={{-120,-220},{120,140}})));
      end partialStore;

      block StoreIsland
          "This store model is used for islanding mode optimization"
        parameter Modelica.SIunits.Temperature Trtu_west_0
          "Initial temperature of rtu west zone";
        parameter Modelica.SIunits.Temperature Trtu_east_0
          "Initial temperature of rtu east zone";
        parameter Modelica.SIunits.Temperature Tref_0
          "Initial temperature of ref zone";
        parameter Modelica.SIunits.Temperature Tfre_0
          "Initial temperature of fre zone";
        parameter Modelica.SIunits.Power PBattery = 0
          "Measured battery power";

        BaseClasses.Thermal thermal(
          Rrtu_west=0.0005,
          Rrtu_east=0.0005,
          Rwest_east=0.01,
        Trtu_west_0 = Trtu_west_0,
        Trtu_east_0 = Trtu_east_0,
          Cref=1e7,
          Rref=0.01,
        Tref_0 = Tref_0,
          Cfre=1e7,
          Rfre=0.02,
          FreHeatingCap=4500,
        Tfre_0 = Tfre_0,
          Rref_fre=0.018)
          annotation (Placement(transformation(extent={{-52,-20},{-32,0}})));
        PV.Simple simple(A=300)
          annotation (Placement(transformation(extent={{-52,50},{-32,70}})));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul
          "Outdoor dry bulb temperature" annotation (Placement(transformation(
                extent={{-140,60},{-100,100}}), iconTransformation(extent={{-120,80},
                  {-100,100}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaPv
          "plane of array solar radiation on pv" annotation (Placement(
              transformation(extent={{-140,30},{-100,70}}), iconTransformation(
                extent={{-120,50},{-100,70}})));
        Modelica.Blocks.Interfaces.RealInput weaPoaWin
          "plane of array solar radiation on Windows" annotation (Placement(
              transformation(extent={{-140,0},{-100,40}}), iconTransformation(
                extent={{-120,20},{-100,40}})));
        Modelica.Blocks.Interfaces.RealInput uHeat "RTU heating signal input"
          annotation (Placement(transformation(extent={{-140,-30},{-100,10}}),
              iconTransformation(extent={{-120,-10},{-100,10}})));
        Modelica.Blocks.Interfaces.RealInput uCool "RTU cooling signal input"
          annotation (Placement(transformation(extent={{-140,-60},{-100,-20}}),
              iconTransformation(extent={{-120,-40},{-100,-20}})));
        Modelica.Blocks.Interfaces.RealInput uRef
        "Cooling signal input for refrigerator"
        annotation (Placement(transformation(extent={{-140,-90},{-100,-50}}),
              iconTransformation(extent={{-120,-70},{-100,-50}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
          "Cooling signal input for freezer"
        annotation (Placement(transformation(extent={{-140,-120},{-100,-80}}),
              iconTransformation(extent={{-120,-100},{-100,-80}})));
        Modelica.Blocks.Interfaces.RealOutput Ppv "Power generated by PV system"
          annotation (Placement(transformation(extent={{100,86},{120,106}}),
              iconTransformation(extent={{100,86},{114,100}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_west
          "RTU electrical power consumption" annotation (Placement(
              transformation(extent={{100,70},{120,90}}), iconTransformation(
                extent={{100,70},{114,84}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu_east
          "RTU electrical power consumption" annotation (Placement(
              transformation(extent={{100,56},{120,76}}), iconTransformation(
                extent={{100,54},{114,68}})));
        Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
        annotation (Placement(transformation(extent={{100,42},{120,62}}),
              iconTransformation(extent={{100,38},{114,52}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
        annotation (Placement(transformation(extent={{100,30},{120,50}}),
              iconTransformation(extent={{100,22},{114,36}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_west "RTU gas power"
          annotation (Placement(transformation(extent={{100,14},{120,34}}),
              iconTransformation(extent={{100,8},{114,22}})));
        Modelica.Blocks.Interfaces.RealOutput Grtu_east "RTU gas power"
          annotation (Placement(transformation(extent={{100,-2},{120,18}}),
              iconTransformation(extent={{100,-8},{114,6}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet
          annotation (Placement(transformation(extent={{100,-18},{120,2}}),
              iconTransformation(extent={{100,-24},{114,-10}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_west
          "Rtu zone air temperature" annotation (Placement(transformation(
                extent={{100,-58},{120,-38}}), iconTransformation(extent={{100,-40},
                  {114,-26}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu_east
          "Rtu zone air temperature" annotation (Placement(transformation(
                extent={{100,-76},{120,-56}}),  iconTransformation(extent={{100,-58},
                  {114,-44}})));
        Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
        annotation (Placement(transformation(extent={{100,-90},{120,-70}}),
              iconTransformation(extent={{100,-78},{114,-64}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
        annotation (Placement(transformation(extent={{100,-104},{120,-84}}),
              iconTransformation(extent={{100,-100},{114,-86}})));
        Modelica.Blocks.Math.MultiSum multiSum(nu=8)
          annotation (Placement(transformation(extent={{32,-66},{44,-54}})));
        Modelica.Blocks.Math.Gain gain(k=-1)
          annotation (Placement(transformation(extent={{-12,30},{8,50}})));
        Modelica.Blocks.Math.Gain gain1(k=0.25)
          annotation (Placement(transformation(extent={{-12,-50},{8,-30}})));
        Modelica.Blocks.Math.Gain gain2(k=0.25)
          annotation (Placement(transformation(extent={{-12,-80},{8,-60}})));
        Modelica.Blocks.Sources.Constant uFreDef(k=0) "Freezer defrost control"
          annotation (Placement(transformation(extent={{-80,-100},{-60,-80}})));
        Modelica.Blocks.Math.Gain gain3(k=0.001/3600)
          "Scale energy unit from jour to kWh"
          annotation (Placement(transformation(extent={{52,-48},{72,-28}})));
      equation
        connect(weaPoaPv, simple.Iinc)   annotation (Line(points={{-120,50},{
                -82,50},{-82,60},{-54,60}},             color={0,0,127}));
        connect(simple.Pgen, Ppv) annotation (Line(points={{-30.8,60},{42,60},{
                42,96},{110,96}}, color={0,0,127}));
        connect(weaTDryBul, thermal.Tout) annotation (Line(points={{-120,80},{
                -80,80},{-80,-0.1},{-52.7,-0.1}}, color={0,0,127}));
        connect(weaPoaWin, thermal.poaWin) annotation (Line(points={{-120,20},{
                -84,20},{-84,-2.3},{-52.7,-2.3}}, color={0,0,127}));
        connect(uHeat, thermal.uHeatWest) annotation (Line(points={{-120,-10},{
                -88,-10},{-88,-4.7},{-52.7,-4.7}},
                                                 color={0,0,127}));
        connect(uCool, thermal.uCoolWest) annotation (Line(points={{-120,-40},{
                -86,-40},{-86,-7.1},{-52.7,-7.1}}, color={0,0,127}));
        connect(uHeat, thermal.uHeatEast) annotation (Line(points={{-120,-10},{
                -88,-10},{-88,-9.5},{-52.7,-9.5}},
                                                 color={0,0,127}));
        connect(uCool, thermal.uCoolEast) annotation (Line(points={{-120,-40},{
                -86,-40},{-86,-11.9},{-52.7,-11.9}}, color={0,0,127}));
        connect(uRef, thermal.uRef) annotation (Line(points={{-120,-70},{-84,
                -70},{-84,-14.9},{-52.7,-14.9}}, color={0,0,127}));
        connect(uFreCool, thermal.uFreCool) annotation (Line(points={{-120,-100},
                {-82,-100},{-82,-19.9},{-52.7,-19.9}},color={0,0,127}));
        connect(thermal.Trtu_west, Trtu_west) annotation (Line(points={{-31.3,
                -0.7},{72,-0.7},{72,-48},{110,-48}}, color={0,0,127}));
        connect(thermal.Grtu_west, Grtu_west) annotation (Line(points={{-31.3,
                -4.7},{68,-4.7},{68,24},{110,24}}, color={0,0,127}));
        connect(thermal.Prtu_west, Prtu_west) annotation (Line(points={{-31.3,
                -2.9},{62,-2.9},{62,80},{110,80}}, color={0,0,127}));
        connect(thermal.Trtu_east, Trtu_east) annotation (Line(points={{-31.3,
                -8.1},{68,-8.1},{68,-66},{110,-66}}, color={0,0,127}));
        connect(thermal.Prtu_east, Prtu_east) annotation (Line(points={{-31.3,
                -9.9},{58,-9.9},{58,66},{110,66}}, color={0,0,127}));
        connect(thermal.Grtu_east, Grtu_east) annotation (Line(points={{-31.3,
                -11.7},{54,-11.7},{54,8},{110,8}}, color={0,0,127}));
        connect(thermal.Tref, Tref) annotation (Line(points={{-31.3,-13.5},{62,
                -13.5},{62,-80},{110,-80}}, color={0,0,127}));
        connect(thermal.Pref, Pref) annotation (Line(points={{-31.3,-15.5},{48,
                -15.5},{48,52},{110,52}}, color={0,0,127}));
        connect(thermal.Tfre, Tfre) annotation (Line(points={{-31.3,-17.5},{58,
                -17.5},{58,-94},{110,-94}}, color={0,0,127}));
        connect(thermal.Pfre, Pfre) annotation (Line(points={{-31.3,-19.3},{42,
                -19.3},{42,40},{110,40}}, color={0,0,127}));
        connect(thermal.Prtu_west, multiSum.u[1]) annotation (Line(points={{-31.3,
                -2.9},{28,-2.9},{28,-56.325},{32,-56.325}},       color={0,0,
                127}));
        connect(thermal.Prtu_east, multiSum.u[2]) annotation (Line(points={{-31.3,
                -9.9},{26,-9.9},{26,-57.375},{32,-57.375}},       color={0,0,
                127}));
        connect(thermal.Pref, multiSum.u[3]) annotation (Line(points={{-31.3,
                -15.5},{24,-15.5},{24,-58.425},{32,-58.425}}, color={0,0,127}));
        connect(thermal.Pfre, multiSum.u[4]) annotation (Line(points={{-31.3,
                -19.3},{22,-19.3},{22,-59.475},{32,-59.475}}, color={0,0,127}));
        connect(simple.Pgen, gain.u) annotation (Line(points={{-30.8,60},{-22,
                60},{-22,40},{-14,40}},color={0,0,127}));
        connect(gain.y, multiSum.u[5]) annotation (Line(points={{9,40},{20,40},
                {20,-60.525},{32,-60.525}}, color={0,0,127}));
        connect(thermal.Pload, multiSum.u[6]) annotation (Line(points={{-31.3,
                -6.3},{18,-6.3},{18,-62},{32,-62},{32,-61.575}}, color={0,0,127}));
        connect(thermal.Grtu_west, gain1.u) annotation (Line(points={{-31.3,
                -4.7},{-20,-4.7},{-20,-40},{-14,-40}},
                                                    color={0,0,127}));
        connect(thermal.Grtu_east, gain2.u) annotation (Line(points={{-31.3,
                -11.7},{-22,-11.7},{-22,-70},{-14,-70}},color={0,0,127}));
        connect(gain1.y, multiSum.u[7]) annotation (Line(points={{9,-40},{14,
                -40},{14,-62.625},{32,-62.625}}, color={0,0,127}));
        connect(gain2.y, multiSum.u[8]) annotation (Line(points={{9,-70},{14,
                -70},{14,-63.675},{32,-63.675}}, color={0,0,127}));
        connect(uFreDef.y, thermal.uFreDef) annotation (Line(points={{-59,-90},
                {-56,-90},{-56,-17.3},{-52.7,-17.3}},
                                            color={0,0,127}));
        connect(gain3.y, Pnet) annotation (Line(points={{73,-38},{80,-38},{80,
                -8},{110,-8}}, color={0,0,127}));
        connect(multiSum.y, gain3.u) annotation (Line(points={{45.02,-60},{50,
                -60},{50,-46},{44,-46},{44,-38},{50,-38}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={255,255,255},
                fillPattern=FillPattern.Solid),
              Text(
                extent={{-248,176},{252,116}},
                textString="%name",
                lineColor={0,0,255})}),           Diagram(coordinateSystem(
                preserveAspectRatio=false, extent={{-100,-120},{100,100}})));
      end StoreIsland;
    end BaseClasses;

    package Validation
      model Store
        extends Modelica.Icons.Example;
        Modelica.Blocks.Sources.CombiTimeTable weather(
          tableOnFile=true,
          tableName="weather_input",
          fileName=
              "/home/kun/Documents/SolarPlus-Optimizer/controller/validation/weather_input.csv",
          columns={2,3,4,5})
          annotation (Placement(transformation(extent={{-60,20},{-40,40}})));

        Building.Optimization.Store store(
          Trtu_west_0(displayUnit="K") = 298.4694438087,
          Trtu_east_0(displayUnit="K")=298.4694438087,
          Tref_0(displayUnit="K") = 276.4833333333,
          Tfre_0(displayUnit="K") = 253.7055555556)
          annotation (Placement(transformation(extent={{0,-4},{20,28}})));
        Modelica.Blocks.Sources.CombiTimeTable Normalized_power_input(
          tableOnFile=true,
          tableName="normalized_power_input",
          fileName=
              "/home/kun/Documents/SolarPlus-Optimizer/controller/validation/normalized_power_input.csv",
          columns={2,3,4,5,6})
          annotation (Placement(transformation(extent={{-60,-20},{-40,0}})));

        Modelica.Blocks.Sources.CombiTimeTable temperature_meas(
          tableOnFile=true,
          tableName="temperature_meas",
          fileName=
              "/home/kun/Documents/SolarPlus-Optimizer/controller/validation/temperature_meas.csv",
          columns={2,3,4,5})
          annotation (Placement(transformation(extent={{-60,-60},{-40,-40}})));

      equation
        connect(weather.y[4], store.weaTDryBul) annotation (Line(points={{-39,30},{-20,
                30},{-20,28},{-1.66667,28}},
                                       color={0,0,127}));
        connect(weather.y[3], store.weaPoaWin) annotation (Line(points={{-39,30},
                {-20,30},{-20,24.6316},{-1.66667,24.6316}},
                                       color={0,0,127}));
        connect(weather.y[2], store.weaPoaPv) annotation (Line(points={{-39,30},{
                -20,30},{-20,21.2632},{-1.66667,21.2632}},
                                   color={0,0,127}));
        connect(Normalized_power_input.y[4], store.uHeat) annotation (Line(points=
               {{-39,-10},{-20,-10},{-20,14.5263},{-1.66667,14.5263}}, color={0,0,
                127}));
        connect(Normalized_power_input.y[1], store.uCool) annotation (Line(points=
               {{-39,-10},{-20,-10},{-20,11.1579},{-1.66667,11.1579}}, color={0,0,
                127}));
        connect(Normalized_power_input.y[5], store.uBattery) annotation (Line(
              points={{-39,-10},{-20,-10},{-20,4.42105},{-1.66667,4.42105}},
                                                               color={0,0,127}));
        connect(Normalized_power_input.y[3], store.uRef) annotation (Line(points={{-39,-10},
                {-20,-10},{-20,1.05263},{-1.66667,1.05263}},
                                                          color={0,0,127}));
        connect(Normalized_power_input.y[2], store.uFreCool) annotation (Line(
              points={{-39,-10},{-20,-10},{-20,-2.31579},{-1.66667,-2.31579}},
                                                             color={0,0,127}));
        connect(Normalized_power_input.y[4], store.uHeatEast) annotation (Line(
              points={{-39,-10},{-20,-10},{-20,17.8947},{-1.66667,17.8947}},
              color={0,0,127}));
        connect(Normalized_power_input.y[1], store.uCoolEast) annotation (Line(
              points={{-39,-10},{-20,-10},{-20,7.78947},{-1.66667,7.78947}},
              color={0,0,127}));
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)),
          experiment(StopTime=1296000, Interval=300));
      end Store;
    end Validation;
  end Building;

annotation (uses(
      Modelica(version="3.2.3"),
      Buildings(version="7.0.0")));
end SolarPlus;
