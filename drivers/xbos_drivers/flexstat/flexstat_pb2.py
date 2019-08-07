# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: flexstat.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import nullabletypes_pb2 as nullabletypes__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='flexstat.proto',
  package='xbospb',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0e\x66lexstat.proto\x12\x06xbospb\x1a\x13nullabletypes.proto\"\xcc\n\n\rFlexstatState\x12)\n\x11space_temp_sensor\x18\x01 \x01(\x0b\x32\x0e.xbospb.Double\x12,\n\x14minimum_proportional\x18\x02 \x01(\x0b\x32\x0e.xbospb.Double\x12,\n\x14\x61\x63tive_cooling_setpt\x18\x03 \x01(\x0b\x32\x0e.xbospb.Double\x12,\n\x14\x61\x63tive_heating_setpt\x18\x04 \x01(\x0b\x32\x0e.xbospb.Double\x12+\n\x13unocc_cooling_setpt\x18\x05 \x01(\x0b\x32\x0e.xbospb.Double\x12+\n\x13unocc_heating_setpt\x18\x06 \x01(\x0b\x32\x0e.xbospb.Double\x12)\n\x11occ_min_clg_setpt\x18\x07 \x01(\x0b\x32\x0e.xbospb.Double\x12)\n\x11occ_max_htg_setpt\x18\x08 \x01(\x0b\x32\x0e.xbospb.Double\x12&\n\x0eoverride_timer\x18\t \x01(\x0b\x32\x0e.xbospb.Double\x12)\n\x11occ_cooling_setpt\x18\n \x01(\x0b\x32\x0e.xbospb.Double\x12)\n\x11occ_heating_setpt\x18\x0b \x01(\x0b\x32\x0e.xbospb.Double\x12*\n\x12\x63urrent_mode_setpt\x18\x0c \x01(\x0b\x32\x0e.xbospb.Double\x12 \n\x08ui_setpt\x18\r \x01(\x0b\x32\x0e.xbospb.Double\x12$\n\x0c\x63ooling_need\x18\x0e \x01(\x0b\x32\x0e.xbospb.Double\x12$\n\x0cheating_need\x18\x0f \x01(\x0b\x32\x0e.xbospb.Double\x12+\n\x13unocc_min_clg_setpt\x18\x10 \x01(\x0b\x32\x0e.xbospb.Double\x12+\n\x13unocc_max_htg_setpt\x18\x11 \x01(\x0b\x32\x0e.xbospb.Double\x12&\n\x0emin_setpt_diff\x18\x12 \x01(\x0b\x32\x0e.xbospb.Double\x12\'\n\x0fmin_setpt_limit\x18\x13 \x01(\x0b\x32\x0e.xbospb.Double\x12\"\n\nspace_temp\x18\x14 \x01(\x0b\x32\x0e.xbospb.Double\x12$\n\x0c\x63ooling_prop\x18\x15 \x01(\x0b\x32\x0e.xbospb.Double\x12$\n\x0cheating_prop\x18\x16 \x01(\x0b\x32\x0e.xbospb.Double\x12$\n\x0c\x63ooling_intg\x18\x17 \x01(\x0b\x32\x0e.xbospb.Double\x12$\n\x0cheating_intg\x18\x18 \x01(\x0b\x32\x0e.xbospb.Double\x12\x19\n\x03\x66\x61n\x18\x19 \x01(\x0b\x32\x0c.xbospb.Bool\x12$\n\x0eoccupancy_mode\x18\x1a \x01(\x0b\x32\x0c.xbospb.Bool\x12)\n\x13setpt_override_mode\x18\x1b \x01(\x0b\x32\x0c.xbospb.Bool\x12\x1f\n\tfan_alarm\x18\x1c \x01(\x0b\x32\x0c.xbospb.Bool\x12\x1e\n\x08\x66\x61n_need\x18\x1d \x01(\x0b\x32\x0c.xbospb.Bool\x12*\n\x14heating_cooling_mode\x18\x1e \x01(\x0b\x32\x0c.xbospb.Bool\x12%\n\x0focc_fan_auto_on\x18\x1f \x01(\x0b\x32\x0c.xbospb.Bool\x12\'\n\x11unocc_fan_auto_on\x18  \x01(\x0b\x32\x0c.xbospb.Bool\x12 \n\nfan_status\x18! \x01(\x0b\x32\x0c.xbospb.Bool\x12\x0c\n\x04time\x18\" \x01(\x04\x62\x06proto3')
  ,
  dependencies=[nullabletypes__pb2.DESCRIPTOR,])




_FLEXSTATSTATE = _descriptor.Descriptor(
  name='FlexstatState',
  full_name='xbospb.FlexstatState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='space_temp_sensor', full_name='xbospb.FlexstatState.space_temp_sensor', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='minimum_proportional', full_name='xbospb.FlexstatState.minimum_proportional', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='active_cooling_setpt', full_name='xbospb.FlexstatState.active_cooling_setpt', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='active_heating_setpt', full_name='xbospb.FlexstatState.active_heating_setpt', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='unocc_cooling_setpt', full_name='xbospb.FlexstatState.unocc_cooling_setpt', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='unocc_heating_setpt', full_name='xbospb.FlexstatState.unocc_heating_setpt', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='occ_min_clg_setpt', full_name='xbospb.FlexstatState.occ_min_clg_setpt', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='occ_max_htg_setpt', full_name='xbospb.FlexstatState.occ_max_htg_setpt', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='override_timer', full_name='xbospb.FlexstatState.override_timer', index=8,
      number=9, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='occ_cooling_setpt', full_name='xbospb.FlexstatState.occ_cooling_setpt', index=9,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='occ_heating_setpt', full_name='xbospb.FlexstatState.occ_heating_setpt', index=10,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='current_mode_setpt', full_name='xbospb.FlexstatState.current_mode_setpt', index=11,
      number=12, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ui_setpt', full_name='xbospb.FlexstatState.ui_setpt', index=12,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cooling_need', full_name='xbospb.FlexstatState.cooling_need', index=13,
      number=14, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='heating_need', full_name='xbospb.FlexstatState.heating_need', index=14,
      number=15, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='unocc_min_clg_setpt', full_name='xbospb.FlexstatState.unocc_min_clg_setpt', index=15,
      number=16, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='unocc_max_htg_setpt', full_name='xbospb.FlexstatState.unocc_max_htg_setpt', index=16,
      number=17, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='min_setpt_diff', full_name='xbospb.FlexstatState.min_setpt_diff', index=17,
      number=18, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='min_setpt_limit', full_name='xbospb.FlexstatState.min_setpt_limit', index=18,
      number=19, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='space_temp', full_name='xbospb.FlexstatState.space_temp', index=19,
      number=20, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cooling_prop', full_name='xbospb.FlexstatState.cooling_prop', index=20,
      number=21, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='heating_prop', full_name='xbospb.FlexstatState.heating_prop', index=21,
      number=22, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cooling_intg', full_name='xbospb.FlexstatState.cooling_intg', index=22,
      number=23, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='heating_intg', full_name='xbospb.FlexstatState.heating_intg', index=23,
      number=24, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fan', full_name='xbospb.FlexstatState.fan', index=24,
      number=25, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='occupancy_mode', full_name='xbospb.FlexstatState.occupancy_mode', index=25,
      number=26, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='setpt_override_mode', full_name='xbospb.FlexstatState.setpt_override_mode', index=26,
      number=27, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fan_alarm', full_name='xbospb.FlexstatState.fan_alarm', index=27,
      number=28, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fan_need', full_name='xbospb.FlexstatState.fan_need', index=28,
      number=29, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='heating_cooling_mode', full_name='xbospb.FlexstatState.heating_cooling_mode', index=29,
      number=30, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='occ_fan_auto_on', full_name='xbospb.FlexstatState.occ_fan_auto_on', index=30,
      number=31, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='unocc_fan_auto_on', full_name='xbospb.FlexstatState.unocc_fan_auto_on', index=31,
      number=32, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fan_status', full_name='xbospb.FlexstatState.fan_status', index=32,
      number=33, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='time', full_name='xbospb.FlexstatState.time', index=33,
      number=34, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=48,
  serialized_end=1404,
)

_FLEXSTATSTATE.fields_by_name['space_temp_sensor'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['minimum_proportional'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['active_cooling_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['active_heating_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['unocc_cooling_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['unocc_heating_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['occ_min_clg_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['occ_max_htg_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['override_timer'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['occ_cooling_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['occ_heating_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['current_mode_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['ui_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['cooling_need'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['heating_need'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['unocc_min_clg_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['unocc_max_htg_setpt'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['min_setpt_diff'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['min_setpt_limit'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['space_temp'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['cooling_prop'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['heating_prop'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['cooling_intg'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['heating_intg'].message_type = nullabletypes__pb2._DOUBLE
_FLEXSTATSTATE.fields_by_name['fan'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['occupancy_mode'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['setpt_override_mode'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['fan_alarm'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['fan_need'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['heating_cooling_mode'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['occ_fan_auto_on'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['unocc_fan_auto_on'].message_type = nullabletypes__pb2._BOOL
_FLEXSTATSTATE.fields_by_name['fan_status'].message_type = nullabletypes__pb2._BOOL
DESCRIPTOR.message_types_by_name['FlexstatState'] = _FLEXSTATSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FlexstatState = _reflection.GeneratedProtocolMessageType('FlexstatState', (_message.Message,), dict(
  DESCRIPTOR = _FLEXSTATSTATE,
  __module__ = 'flexstat_pb2'
  # @@protoc_insertion_point(class_scope:xbospb.FlexstatState)
  ))
_sym_db.RegisterMessage(FlexstatState)


# @@protoc_insertion_point(module_scope)
