import xadmin

from . import models


class ResourceAdmin:
    list_filter = ['resource_type', 'name']
    list_display = ['id', 'name', 'resource_type', 'resource_type_sec']
    ordering = ['id', 'name']


class FlightInfoAdmin:
    list_filter = ['arrival_departure_flag', 'flight_number']
    list_display = ['flight_number', 'plan_takeoff', 'estimate_takeoff']
    ordering = ['id']


class FlightResourceAdmin:
    list_display = ['flight', 'resource', 'plan_start_time', 'plan_end_time',
                    'actual_start_time', 'actual_end_time', 'is_using']
    ordering = ['id', '-plan_start_time']
    list_filter = ['resource__resource_type', 'flight', 'resource__name']
    list_editable = ['is_using']


class AirportAdmin:
    list_display = ['three_code', 'four_code', 'property', 'ch_description', 'inter_description', 'is_open']
    list_filter = ['ch_description']
    ordering = ['id']


xadmin.site.register(models.ResourceInfo, ResourceAdmin)
xadmin.site.register(models.FlightInfo, FlightInfoAdmin)
xadmin.site.register(models.PassageWayCarPassThrough)
xadmin.site.register(models.FlightResource, FlightResourceAdmin)
xadmin.site.register(models.FlightException)
xadmin.site.register(models.FlightCompany)
xadmin.site.register(models.Airport, AirportAdmin)
