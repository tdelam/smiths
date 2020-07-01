# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'UserProfile.shipping_zip_postal'
        db.delete_column('accounts_userprofile', 'shipping_zip_postal')

        # Deleting field 'UserProfile.shipping_state_province'
        db.delete_column('accounts_userprofile', 'shipping_state_province')

        # Deleting field 'UserProfile.user'
        db.delete_column('accounts_userprofile', 'user_id')

        # Deleting field 'UserProfile.shipping_city'
        db.delete_column('accounts_userprofile', 'shipping_city')

        # Adding field 'UserProfile.contact'
        db.add_column('accounts_userprofile', 'contact',
                      self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'UserProfile.shipping_zip_postal'
        db.add_column('accounts_userprofile', 'shipping_zip_postal',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.shipping_state_province'
        db.add_column('accounts_userprofile', 'shipping_state_province',
                      self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.user'
        db.add_column('accounts_userprofile', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['auth.User'], unique=True),
                      keep_default=False)

        # Adding field 'UserProfile.shipping_city'
        db.add_column('accounts_userprofile', 'shipping_city',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'UserProfile.contact'
        db.delete_column('accounts_userprofile', 'contact')


    models = {
        'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'billing_address_1': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'billing_address_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'billing_city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'billing_country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'billing_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'billing_state_province': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'billing_zip_postal': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'shipping_address_1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping_address_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['accounts']