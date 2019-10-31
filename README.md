# cf5202-python

usage: cf5202.py [-h] [-bs {00,01}] [-we WRITE_EPC] [-i] [-srp SET_RF_POWER]
                 [-cb] [-rd] [-bi] [-er] [-sti] [-gbd] [-gri]

optional arguments:
  -h, --help            show this help message and exit
  -bs {00,01}, --beep_setting {00,01}
                        Beep setting 00,01.
  -we WRITE_EPC, --write_epc WRITE_EPC
                        Write EPC - max 20 characters.
  -i, --inventory       Print EPC inventory.
  -srp SET_RF_POWER, --set_rf_power SET_RF_POWER
                        Set RF power - 00-1e
  -cb, --clear_buffer
  -rd, --read_data
  -bi, --buffer_inventory
  -er, --extension_read
  -sti, --single_tag_inventory
  -gbd, --get_buffer_data
  -gri, --get_reader_information
