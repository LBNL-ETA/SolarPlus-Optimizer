within MPC;
package HVACR "Package for HVAC models"
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
