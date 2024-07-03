from __future__ import unicode_literals
from django.contrib.gis.db import models

class Timezone(models.Model):
    tzid = models.CharField(max_length=80)
    geom = models.PolygonField(srid=4326)

    def __unicode__(self):
        return unicode(self.tzid)

timezone_mapping = {
    'tzid': 'TZID',
    'geom': 'POLYGON',
}