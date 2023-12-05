# cf5202-python
Chafon RFID reader

usage: cf5202.py [-h] [-bs {00,01}] [-we WRITE_EPC] [-i] [-srp SET_RF_POWER]
                 [-cb] [-rd] [-bi] [-er] [-sti] [-gbd] [-gri]

optional arguments:<br>
  -h, --help            show this help message and exit<br>
  -bs {00,01}, --beep_setting {00,01}<br>
                        Beep setting 00,01.<br>
  -we WRITE_EPC, --write_epc WRITE_EPC<br>
                        Write EPC - max 20 characters.<br>
  -i, --inventory       Print EPC inventory.<br>
  -srp SET_RF_POWER, --set_rf_power SET_RF_POWER<br>
                        Set RF power - 00-1e<br>
  -cb, --clear_buffer<br>
  -rd, --read_data<br>
  -bi, --buffer_inventory<br>
  -er, --extension_read<br>
  -sti, --single_tag_inventory<br>
  -gbd, --get_buffer_data<br>
  -gri, --get_reader_information<br> 

pip install crcmod pyserial coreapi
