# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Option'
        db.create_table('object_config_option', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('help_text', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('opt_value', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('default_value', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('object_config', ['Option'])

        # Adding unique constraint on 'Option', fields ['content_type', 'object_id', 'name']
        db.create_unique('object_config_option', ['content_type_id', 'object_id', 'name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Option', fields ['content_type', 'object_id', 'name']
        db.delete_unique('object_config_option', ['content_type_id', 'object_id', 'name'])

        # Deleting model 'Option'
        db.delete_table('object_config_option')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'object_config.option': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'name'),)", 'object_name': 'Option'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'default_value': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'help_text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'opt_value': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['object_config']
