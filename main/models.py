# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class VCenter(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    ip = models.CharField(max_length=16, blank=True, null=True)
    user = models.CharField(max_length=32, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    remarks = models.CharField(verbose_name='备注',max_length=255, blank=True, null=True)
    exsi_version = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'v_center'
        verbose_name_plural = '宿主机'

    def __str__(self):
        return self.name

class Vms(models.Model):
    name = models.CharField(verbose_name='名称', max_length=128, blank=True, null=True, db_index=True)
    vmpathname = models.CharField(max_length=128, blank=True, null=True)
    guestfullname = models.CharField(max_length=128, blank=True, null=True)
    annotation = models.CharField(max_length=255, blank=True, null=True)
    powerstate = models.CharField(verbose_name='电源状态', max_length=12, blank=True, null=True)
    ipaddress = models.CharField(max_length=16, blank=True, null=True)
    des = models.CharField(verbose_name='描述', max_length=512, blank=True, null=True)
    numcpu = models.IntegerField(blank=True, null=True)
    memorysizemb = models.IntegerField(blank=True, null=True)
    user = models.CharField(max_length=12, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    uuid = models.CharField('VM-uuid', max_length=36, db_index=True, blank=True, null=True)
    createTime = models.DateField(auto_now_add=True)
    vcent = models.ForeignKey(
        'VCenter',
        on_delete=models.CASCADE,
    )
    class Meta:
        managed = True
        db_table = 'vms'
        verbose_name_plural = '虚拟机'

    def __str__(self):
        return self.name