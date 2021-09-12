# About Infra Red

## IR recording

### light on
python3 irrp.py -r -g4 -f codes light::on --no-confirm --post 130

### light off
python3 irrp.py -r -g4 -f codes2 light::off --no-confirm --post 130

### aircon on (除湿)
python3 irrp.py -r -g4 -f codes3 aircon::on --no-confirm --post 130

### aircon off
python3 irrp.py -r -g4 -f codes4 aircon::off --no-confirm --post 130

### light dark
python3 irrp.py -r -g4 -f codes5 light::dark --no-confirm --post 130

### light bright
python3 irrp.py -r -g4 -f codes6 light::bright --no-confirm --post 130

### light warm
python3 irrp.py -r -g4 -f codes7 light::warm --no-confirm --post 130

### light white
python3 irrp.py -r -g4 -f codes8 light::white --no-confirm --post 130


## IR sending
python3 irrp.py -p -g13 -f codes light::on
python3 irrp.py -p -g13 -f codes2 light::off
python3 irrp.py -p -g13 -f codes5 light::dark
python3 irrp.py -p -g13 -f codes6 light::bright
python3 irrp.py -p -g13 -f codes7 light::warm
python3 irrp.py -p -g13 -f codes8 light::white

