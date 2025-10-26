#!/bin/python3.8
import time
import ipaddress, socket
import os, platform, subprocess
#import multiprocessing
#from multiprocessing import Process
from threading import Thread as Process
from icmplib import ping, multiping, traceroute, Host, Hop
socket.setdefaulttimeout(0.1)

class queue:
    cores           = int(0)    # number of cores of a system
    max_processes   = int(0)    # ping threds per core
    ip_list         = []        # list of ip-adresses
    job_list        = []        # list of jobs
    job_active_list = []        # list of current active jobs
    host_list       = []

    def __init__(self):
        self.cores = 4
        self.max_processes = self.cores * 10

    # Funktion zur Statusabfrage der aktuellen Jobs, die laufen
    def status(self):
        status_string = "Jobs - ACTIVE:{} - MAX:{}-".format(len(self.job_list),len(self.cores*max_processes))
        print(status_string)

    # Funktion zum initiieren der Jobliste
    def init_jobs(self):
        counter = int(0)
        for ipaddr in self.ip_list:
            exec_string = "self.p{} = Process(target=self.get_ip_up_down, args=('{}',))".format(counter,ipaddr)
            job_id      = "self.p{}".format(counter)
            self.job_list.append([job_id,exec_string])
            counter     += 1
            if int(counter) % 2 == 0:
                print("Es befinden sich {} Jobs in der Liste...\r".format(len(self.job_list)))
        counter = int(0)
        all_jobs = len(self.job_list)
        for job in self.job_list:
            print(job[1])
            exec(job[1])
            if int(counter) % 2 == 0:
                print("Jobs werden Initialisiert... {}/{}\r".format(counter, all_jobs))


    # Diese funktion startet die queue.
    # Wenn die queue gestartet wurde, dann fängt sie an die listen abzuarbeiten
    def run(self):
        for job in self.job_list:
            add_done = False
            while add_done == False:
                if int(len(self.job_active_list)) < int(self.max_processes): # Wenn die liste nicht die Maximale anzahl an processes erreicht hat, dann..
                    run_string = "{}.start()".format(job[0])
                    exec(run_string)
                    self.job_active_list.append(job)
                    add_done = True
                elif int(len(self.job_active_list)) >= int(self.max_processes):
                    for active_job in self.job_active_list: # führe das folgende für alle freien plätze in der queue aus:
                        # print("Warte auf Job:", active_job)
                        exec_string = "{}.join()".format(active_job[0])
                        self.job_active_list.pop(0)
                        exec(exec_string)
        for active_job in self.job_active_list: # führe das folgende für alle freien plätze in der queue aus:
            exec_string = "{}.join()".format(active_job[0])
            self.job_active_list.pop(0)
            exec(exec_string)


    def get_ip_up_down(self, ip):
        host = ping(ip, count=1, interval=0.5, timeout=1)
        with open("ping.txt","a") as pingfile:
            if host.is_alive == True:
                pingfile.write("{},UP\n".format(ip))
                pingfile.close()
                print(ip,"UP")
            else:
                pingfile.write("{},DOWN\n".format(ip))
                pingfile.close()
                print(ip,"DOWN")

    # Mit dieser funktion kann man eine IP zu der queue hinzufügen.
    # Nutzen: add_ip_to_list("192.168.188.120")
    def add_ip_to_list(self, ip):
        try:ipaddress.IPv4Network(ip)
        except Exception as e:
            error1 = True
        try:ipaddress.IPv6Network(ip)
        except Exception as f:
            if error1 == True and error2 == True:
                print("Error in queue.add_ip_to_list : {} -- {}".format(e,f))
            else:
                self.ip_list.append = ip


    # Funktion zur generiering von IP Adressen, die in die Liste der queue geschreiben werden.
    # Nutzen: generate_list("10.0.0.0/8", "ipv4")
    def generate_list(self, range, protocol):
        if protocol == "ipv4":
            for ipaddr in ipaddress.IPv4Network(range):
                self.ip_list.append(ipaddr)
            self.ip_list.pop(0) #del first element of list (Netzadresse)
            self.ip_list.pop(-1) #del last element of list (Broadcast)
        elif protocol == "ipv6":
            for ipaddr in ipaddress.IPv6Network(range):
                self.ip_list.append(ipaddr)
            self.ip_list.pop(0) #del first element of list (Netzadresse)
            self.ip_list.pop(-1) #del last element of list (Broadcast)
        else:
            print("Fehler in queue.generate_list : falsche Eingabe.")

    # Funktion zum entladen der Jobliste.
    # Das Ausführen dieser Funktion löscht alle jobs in der queue.
    def drop_job_list(self):
        try:
            del self.job_list
            self.job_list = []
        except Exception as e:
            print("Fehler in queue.drop_job_list:", e)

    # Funktion zum entladen der IPliste
    # Diese Funktion löscht alle IP Adressen aus der queue.
    def drop_ip_list(self):
        try:
            del self.ip_list
            self.ip_list = []
        except Exception as e:
            print("Fehler in queue.drop_ip_list:", e)


class check_ip:
    ip              = ""
    type            = ""
    check_type      = ""
    hostname_list   = []
    ip_pool_list    = []

    # def worker(self):
    #     for ipaddr in ipaddress.IPv4Network(self.ip):
    #         self.ip_pool_list.append(ipaddr)
    #     self.ip_pool_list.pop(0)
    #     self.ip_pool_list.pop(-1)
    #
    #     if __name__ == '__main__':
    #         self.pool = Pool(processes=28)
    #         self.result = pool.apply_async(get_ip_up_down(ip), [len(self.ip_pool_list)])
    #         print(self.result.get(timeout=1))
    #         print(self.pool.map(self.get_ip_up_down, range(len(self.ip_pool_list))))
    #
    #     for i in ip_pool_list:
    #         print(i[0], i[1])


    def get_ip_range_from_user(self):
        if self.check_type == "Reverse":
            while True:
                print("IP-version eingeben IPv(4)/IPv(6):")
                self.type = input("")
                if self.type != "4" and self.type != "6":
                    print("FEHLER: ungültige Eingabe")
                else:
                    print("Bitte IP Range (IPv4: 192.168.2.0/24) (IPv6: fd01::/64) eingeben")
                    self.ip = input("")
                    break
        else:
            print("Hostname eingeben:")
            self.ip = input("")


    def get_dns_lookup_type(self):
        while True:
            print("Lookup Typ eingeben (F)orward/(R)everse:")
            self.check_type = input("")
            if self.check_type == "f" or self.check_type == "F":
                self.check_type = "Forward"
                break
            elif self.check_type == "r" or self.check_type == "R":
                self.check_type = "Reverse"
                break
            else:
                print("FEHLER: ungültige Eingabe")


    def run(self):
        # Run Forward Lookup
        if self.check_type == "Forward":
            print(self.ip, "->" ,socket.gethostbyname(self.ip))
        # Run Reverse Lookups
        elif self.check_type == "Reverse":
            self.hostname_list = []
            # Run Lookups on IPv4
            if self.type == "4":
                for ip in ipaddress.IPv4Network(self.ip):
                        if ip != self.ip:
                            try:
                                lookup = socket.gethostbyaddr(str(ip))
                            except socket.herror:
                                print(ip, " -> No reverse lookup")
                                self.hostname_list.append([ip,ip])
                            else:
                                print(ip, " ->", lookup[0])
                                self.hostname_list.append([ip,lookup[0]])

            # Run Lookups on IPv6
            if self.type == "6":
                self.hostname_list = []
                for ip in ipaddress.IPv6Network(self.ip):
                        if ip != self.ip:
                            try:
                                lookup = socket.gethostbyaddr(str(ip))
                            except socket.herror:
                                print(ip, " -> No reverse lookup")
                            else:
                                print(ip, " ->", lookup[0])
                                self.hostname_list.append([ip,lookup[0]])
            print("\nAlle erfolgreichen DNS Lookups anzeigen??")
            choice = str(input("j/n: "))
            if choice == "j":
                for i in self.hostname_list:
                    print(i[0], "->", i[1])
            else:
                pass
        else:
            print("FEHLER: Falscher DNS Lookup Parameter!")

def main():
    c = check_ip()
    w = queue()
    while True:
        c.get_dns_lookup_type()
        c.get_ip_range_from_user()
        c.run()
        w.generate_list(c.ip, "ipv4")
        w.init_jobs()
        w.run()
        time.sleep(10)

        print("STARTE AUSWERTUNG")
        pingfile = open("ping.txt","r")
        ping_ergebnisse = pingfile.read()
        pingfile.close()
        ping_ergebnisse = ping_ergebnisse.splitlines()
        ping_auswertung = []
        for status in ping_ergebnisse:
            status = status.split(",")
            print(status)
            ping_auswertung.append([status[0],status[1]])
        auswertung = []
        print(len(c.hostname_list))
        for hostname in c.hostname_list:
            for status in ping_auswertung:
                if str(hostname[0]) == str(status[0]):
                    auswertung.append([hostname[0],hostname[1],status[1],status[0]])

        print("auswertung:")
        print("IP;DNS;Status;")
        for i in auswertung:
            print(str(i[0])+";"+str(i[1])+";"+str(i[2])+";")



        time.sleep(1)
        print("Bitte mit ENTER bestätigen:")
        x = input()


if __name__ == "__main__":
    app = main()
