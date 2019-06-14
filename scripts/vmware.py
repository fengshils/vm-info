from __future__ import print_function
import os,sys,django

from django.core.wsgi import get_wsgi_application

# sys.path.extend([r'E:/pythonproject/django_rest_env/mysite',])
sys.path.extend([os.getcwd(),])
os.environ.setdefault("DJANGO_SETTINGS_MODULE","mysite.settings")
application = get_wsgi_application()
django.setup()


from main.models import *



from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import argparse
import atexit
import getpass
import ssl
import  lorm, pymysql

def PrintVmInfo(vm, vcent, depth=1 ):
   """
   Print information for a particular virtual machine or recurse into a folder
   or vApp with depth protection
   """
   maxdepth = 10

   # if this is a group it will have children. if it does, recurse into them
   # and then return
   if hasattr(vm, 'childEntity'):
      if depth > maxdepth:
         return
      vmList = vm.childEntity
      for c in vmList:
         PrintVmInfo(c, depth+1)
      return

   # if this is a vApp, it likely contains child VMs
   # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
   if isinstance(vm, vim.VirtualApp):
      vmList = vm.vm
      for c in vmList:
         PrintVmInfo(c, depth + 1)
      return

   summary = vm.summary
   print("Name       : ", summary.config.name)
   print("Path       : ", summary.config.vmPathName)
   print("Guest      : ", summary.config.guestFullName)
   annotation = summary.config.annotation
   if annotation != None and annotation != "":
      print("Annotation : ", annotation)
   print("State      : ", summary.runtime.powerState)
   if summary.guest != None:
      ip = summary.guest.ipAddress
      if ip != None and ip != "":
         print("IP         : ", ip)
   if summary.runtime.question != None:
      print("Question  : ", summary.runtime.question.text)

   #检测虚拟机在数据库是否存在,
   v1  = Vms.objects.filter(uuid=summary.config.instanceUuid)
   if v1.first():
      v1.update(
          name=summary.config.name,
          powerstate=summary.runtime.powerState
      )
   else:
       v = Vms(name=summary.config.name,
               vmpathname=str(summary.config.vmPathName),
               guestfullname=summary.config.guestFullName,
               annotation=summary.config.annotation,
               powerstate=summary.runtime.powerState,
               ipaddress = summary.guest.ipAddress,
               memorysizemb = summary.config.memorySizeMB,
               uuid=summary.config.instanceUuid,
               vcent=vcent)
       v.save()


def main(vcent):
   context = None
   if hasattr(ssl, '_create_unverified_context'):
      context = ssl._create_unverified_context()
   si = SmartConnect(host=vcent.ip,
                     # user='administrator@vsphere.local',
                     user=vcent.user,
                     pwd=vcent.password,
                     # port=int(args.port),
                     sslContext=context)

   if not si:
       print("Could not connect to the specified host using specified "
             "username and password")
       return -1

   atexit.register(Disconnect, si)
   #检查虚拟在宿主机上是否还存在
   vms = Vms.objects.filter(vcent=vcent).all()
   search_index = si.content.searchIndex
   if vms:
       for v in vms:
           vmv = search_index.FindByUuid(None, v.uuid, True, True)
           print(vmv)
           if vmv is None:
               v.delete()

   #获取每台宿主机上虚拟机列表
   content = si.RetrieveContent()
   for child in content.rootFolder.childEntity:
      if hasattr(child, 'vmFolder'):
         datacenter = child
         vmFolder = datacenter.vmFolder
         vmList = vmFolder.childEntity
         for vm in vmList:
            PrintVmInfo(vm=vm, vcent=vcent)
   return 0

# Start program
if __name__ == "__main__":
    all_Vcenter = VCenter.objects.all()
    for vcent in all_Vcenter:
        # print(vcent)
        # main(vcent)
        try:
            main(vcent)
        except Exception as e:
            print(e)