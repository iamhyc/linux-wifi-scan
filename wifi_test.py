#!/usr/bin/env python3
import iwlist
import threading, queue, time, logging

IFACE='wlp6s0'

def wifi_scan(q):
    delta = 0
    while True:
        t_init = time.time()
        raw_results = iwlist.scan(interface=IFACE) #trigger a scan
        t_end = time.time()
        results = iwlist.parse(raw_results)
        
        jitter = (t_end - t_init) - delta
        delta = t_end - t_init
        q.put_nowait({
            'start':t_init,
            'end':t_end,
            'delta':delta,
            'jitter':jitter,
            'results':results
            })
        pass
    pass

def main_loop(q):
    while True:
        try:
            list = q.get()
            #{timestamp, name, rssi}
            print('%.2f\t%.2f\t%.2f\t%.2f'%(list['start'], list['end'], list['delta'], list['jitter']))
            for item in list['results']:
                print('\tSSID: %s, RSSI: %s'%(item['essid'], item['signal_level_dBm']))
                pass
        except Exception as e:
            pass
        pass
    pass

def main():
    q = queue.Queue()
    t = threading.Thread(target=wifi_scan, args=(q, ))
    t.setDaemon(True)
    t.start()

    main_loop(q)
    
    pass

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(e)
    finally:
        exit()
    