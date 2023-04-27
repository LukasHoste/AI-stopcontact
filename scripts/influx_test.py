from influxdb import InfluxDBClient


flux_client = InfluxDBClient(host= '10.15.51.63', port=8086, username='plug2',password='stop123')
print(flux_client.get_list_database())