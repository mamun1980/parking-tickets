from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from tgis.forms import addressForm
from django.db.models import *
from tgis.models import Paths, Tickets
from django.contrib.gis.geos import fromstr


def home(request):
	adForm = addressForm()	
	if request.method == 'POST':
		if 'chance_of_ticket' in request.POST:
			address = request.POST['address']
			stime = request.POST['start_time']
			etime = request.POST['end_time']
			dname = request.POST['day_of_week']
			#import pdb; pdb.set_trace()
			if address:
				longlat = getPoint(address)
				pnt = fromstr('POINT(%f %f)' % longlat,srid=4269)
			else:
				pnt = fromstr('POINT(-122.398595809937 37.7840061485767)', srid=4269)
			
			ticket_frequency = getTicketFrequency(pnt,stime,etime)
			ticket_frequency['num_patrol'] = 'XXX'
			ticket_frequency['chance_of_ticket'] = '33'

			return render_to_response('home.html',{'TF': ticket_frequency,'address':address,'form': adForm}, context_instance=RequestContext(request))

		elif 'tell_me_the_laws' in request.POST:
			address = request.POST['address']
			if address:					
				getlaws = getLaw(address)
				
				vcounter = []
				for law in getlaws:
					vcounter.append(law['description'])
				from collections import Counter
				vc = Counter(vcounter).most_common(2)
				most_violated_role = vc[0][0]
				sec_most_violated_role = vc[1][0]
				if len(getlaws) == 0:
					getlaws = 'No';
				return render_to_response('home.html',{'form': adForm, 'PL': getlaws, 'mvr': most_violated_role,
				'smvr':sec_most_violated_role, 'address': address}, context_instance=RequestContext(request))
			else:
				getlaws = getLaw('1045 PINE ST, San Francisco, CA')
			return render_to_response('home.html',{'form': adForm, 'PL': getlaws,'address': address}, context_instance=RequestContext(request))

	else:
		return render_to_response('home.html',{'form': adForm,}, context_instance=RequestContext(request))
	

def getPoint(address):
		from geocode.google import GoogleGeocoderClient
		geocoder = GoogleGeocoderClient(False)
		
		result = geocoder.geocode(address)
		if result.is_success():
			longlat = result.get_location()
			lat = float(str(longlat[1]))
			lang = float(str(longlat[0]))
			return lat,lang


def getTicketFrequency(location,stime, etime):
	from time import mktime
	from datetime import datetime
	import pdb; pdb.set_trace()
	try:
		P11 = Paths.objects.filter(path__dwithin=(location, 0.0001))
		# test = []
		# for path in P11:
		# 	if path.start_datetime.time().hour <= int(stime):
		# 		test.append(path)
		# import pdb; pdb.set_trace()
		P1 = P11.aggregate(end_datetime=Max('end_datetime'), start_datetime=Min('start_datetime'), cnt=Count('id'))
		hours = (mktime(datetime.utctimetuple(P1['end_datetime'])) - mktime(datetime.utctimetuple(P1['start_datetime']))) / 3600
		tickets_per_hour = (P1['cnt'] / hours) * 100
		P1['hours'] = hours
		P1['tickets_per_hour'] = tickets_per_hour	
		return P1

	except TypeError:
		return "No"


def getLaw(address):
		from django.db import connection, transaction
		longlat = getPoint(address)
		longlat = longlat + longlat
		cursor = connection.cursor()
		sql = '''select violation, violation_description as description, fine_amt,split_part(location, ' ', 2)
					AS street,ROUND(MAX(ST_Distance_Sphere(geopoint,ST_SetSRID(ST_Point(%s, %s), 4269))))
					AS meters from tickets where ST_DWithin(geopoint, ST_SetSRID(ST_Point(%s, %s), 4269),
					0.0005) group by violation, violation_description, fine_amt, street'''
		cursor.execute(sql,longlat)
		result = dictfetchall(cursor)
		return result
	

def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
