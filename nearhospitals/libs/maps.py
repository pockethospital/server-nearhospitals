import googlemaps

class GoogleMaps:
    gmaps = googlemaps.Client(key='AIzaSyDM_vyEhCa-6XerqhukIXNflsAvpqD7F8c')
    
    def __init__(self, lat, lng):
        self.coordinates = tuple((lat, lng))
        self.reverse_geocode_result = self.gmaps.reverse_geocode(self.coordinates)

    def getAddressComponents(self):
        addressComponents = set(())
        for address in self.reverse_geocode_result:
            for addressComponent in address["address_components"]:
                addressComponents.add({
                    "name": addressComponent['long_name'],
                    "type": "addressComponent['types'][0]"
                })

        return addressComponents