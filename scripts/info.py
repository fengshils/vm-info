#!/opt/python3/bin/python3
#coding:utf-8

"""
获取所有的vcenter相关信息
包括exsi的硬件资源信息和vmware客户端的硬件分配信息
"""
import pymysql
import lorm
import config
db = lorm.Hub(pymysql)
db.add_pool('default', host=config.MYSQL_HOST, port=config.MYSQL_PORT, user=config.MYSQL_USER,
    passwd=config.MYSQL_PASSWORD, db=config.MYSQL_DB, autocommit=True, pool_size=8, wait_timeout=30)


from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
from pprint import pprint
import atexit
import argparse


def get_args():
    args = {'host':'192.168.150.218',
            'user':'root',
            'port': 443,
            'password':'1qaz@WSX'
            }
    return args


def get_obj(content, vimtype, name=None):
    '''
    列表返回,name 可以指定匹配的对象
    '''
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    obj = [ view for view in container.view]
    return obj


def main(v_center):
    esxi_host = {}
    # connect this thing
    si = SmartConnectNoSSL(
            host=v_center['ip'],
            user=v_center['user'],
            pwd=v_center['password'],
            port=443)
    # disconnect this thing
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    esxi_obj = get_obj(content, [vim.HostSystem])
    for esxi in esxi_obj:
        esxi_host[esxi.name] = {'esxi_info':{},'datastore':{}, 'network': {}, 'vm': {}}

        esxi_host[esxi.name]['esxi_info']['厂商'] = esxi.summary.hardware.vendor
        esxi_host[esxi.name]['esxi_info']['型号'] = esxi.summary.hardware.model
        for i in esxi.summary.hardware.otherIdentifyingInfo:
            if isinstance(i, vim.host.SystemIdentificationInfo):
                esxi_host[esxi.name]['esxi_info']['SN'] = i.identifierValue
        esxi_host[esxi.name]['esxi_info']['处理器'] = '数量：%s 核数：%s 线程数：%s 频率：%s ' % (esxi.summary.hardware.numCpuPkgs,
                                                                                      esxi.summary.hardware.numCpuCores,
                                                                                      esxi.summary.hardware.numCpuThreads,
                                                                                      esxi.summary.hardware.cpuMhz)
        db.default.v_center.filter(id=v_center['id']).update(cpu=esxi_host[esxi.name]['esxi_info']['处理器'])
        esxi_host[esxi.name]['esxi_info']['处理器使用率'] = '%.1f%%' % (esxi.summary.quickStats.overallCpuUsage /
                                                       (esxi.summary.hardware.numCpuPkgs * esxi.summary.hardware.numCpuCores * esxi.summary.hardware.cpuMhz) * 100)
        esxi_host[esxi.name]['esxi_info']['内存(MB)'] = esxi.summary.hardware.memorySize/1024/1024
        esxi_host[esxi.name]['esxi_info']['可用内存(MB)'] = '%.1f MB' % ((esxi.summary.hardware.memorySize/1024/1024) - esxi.summary.quickStats.overallMemoryUsage)
        esxi_host[esxi.name]['esxi_info']['内存使用率'] = '%.1f%%' % ((esxi.summary.quickStats.overallMemoryUsage / (esxi.summary.hardware.memorySize/1024/1024)) * 100)
        esxi_host[esxi.name]['esxi_info']['系统'] = esxi.summary.config.product.fullName

        # print(esxi_host[esxi.name]['esxi_info']['内存(MB)'], esxi_host[esxi.name]['esxi_info']['可用内存(MB)'], esxi_host[esxi.name]['esxi_info']['系统'])
        # db.default.v_center.filter(id=v_center['id']).update(memory=esxi_host[esxi.name]['esxi_info']['内存(MB)'],
        #                                                 available_memory = esxi_host[esxi.name]['esxi_info']['可用内存(MB)'],
        #                                                 system = esxi_host[esxi.name]['esxi_info']['系统'],
        #                                                 disk = esxi.datastore,
        #                                                 )
        disk = []
        for ds in esxi.datastore:
            esxi_host[esxi.name]['datastore'][ds.name] = {}
            esxi_host[esxi.name]['datastore'][ds.name]['总容量(G)'] = int((ds.summary.capacity)/1024/1024/1024)
            esxi_host[esxi.name]['datastore'][ds.name]['空闲容量(G)'] = int((ds.summary.freeSpace)/1024/1024/1024)
            esxi_host[esxi.name]['datastore'][ds.name]['类型'] = (ds.summary.type)
        db.default.v_center.filter(id=v_center['id']).update(memory=esxi_host[esxi.name]['esxi_info']['内存(MB)'],
                                                        available_memory = esxi_host[esxi.name]['esxi_info']['可用内存(MB)'],
                                                        system = esxi_host[esxi.name]['esxi_info']['系统'],
                                                        disk = str(esxi_host[esxi.name]['datastore']),
                                                        )
        # for nt in esxi.network:
        #     esxi_host[esxi.name]['network'][nt.name] = {}
        #     esxi_host[esxi.name]['network'][nt.name]['标签ID'] = nt.name
        # for vm in esxi.vm:
        #     esxi_host[esxi.name]['vm'][vm.name] = {}
        #     esxi_host[esxi.name]['vm'][vm.name]['电源状态'] = vm.runtime.powerState
        #     esxi_host[esxi.name]['vm'][vm.name]['CPU(内核总数)'] = vm.config.hardware.numCPU
        #     esxi_host[esxi.name]['vm'][vm.name]['内存(总数MB)'] = vm.config.hardware.memoryMB
        #     esxi_host[esxi.name]['vm'][vm.name]['系统信息'] = vm.config.guestFullName
        #     if vm.guest.ipAddress:
        #         esxi_host[esxi.name]['vm'][vm.name]['IP'] = vm.guest.ipAddress
        #     else:
        #         esxi_host[esxi.name]['vm'][vm.name]['IP'] = '服务器需要开机后才可以获取'
        #
        #     for d in vm.config.hardware.device:
        #         if isinstance(d, vim.vm.device.VirtualDisk):
        #             esxi_host[esxi.name]['vm'][vm.name][d.deviceInfo.label] = str((d.capacityInKB)/1024/1024) + ' GB'




if __name__ == '__main__':
    # main()

    v_centers = db.default.fetchall_dict("select * from v_center")
    for v_center in v_centers:
        print(v_center)
        try:
            main(v_center)
        except BaseException as e:
            print(e)