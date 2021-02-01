import datetime

sample_data = {
        "customers": [
            {  
                "FirstName": "Jen",
                "LastName": "Simpson",
                "ShipToState": "MN",
                "Orders": [
                    {
                        "Product": "Pirate",
                        "ShippingTotal": 12.11,
                        "CreationDate": datetime.datetime(2012, 6, 12),
                        "Items": [
                            {
                                "ProductName": "Pirate",
                                "Quantity": 1,
                                "UnitPrice": 10.25
                            }, 
                            {
                                "ProductName": "Ninja",
                                "Quantity": 3,
                                "UnitPrice": 11.12
                            }
                        ]
                    }, 
                    {
                        "Product": "Monster",
                        "ShippingTotal": 21.98,
                        "CreationDate": datetime.datetime(2013, 6, 1),
                        "Items": [
                            {
                                "ProductName": "Monster",
                                "Quantity": 1,
                                "UnitPrice": 20.50
                            }
                        ]
                    }
                ]
            },
            {
               "FirstName": "Doug",
               "LastName": "Johnson",
               "ShipToState": "MN",
               "Orders": [
                   {
                       "Product": "Ninja",
                       "CreationDate": datetime.datetime(2012, 6, 1),
                       "ShippingTotal": 15.34,
                       "Items": [
                           {
                               "ProductName": "Frog",
                               "Quantity": 2,
                               "UnitPrice": 14.68
                           }
                       ]
                   },
                   {
                       "Product": "Frog",
                       "CreationDate": datetime.datetime(2012, 12, 1),
                       "ShippingTotal": 5,
                       "Items": [
                           {
                               "ProductName": "Sailor",
                               "Quantity": 5,
                               "UnitPrice": 18.32
                           },
                           {
                               "ProductName": "Monster",
                               "Quantity": 1,
                               "UnitPrice": 21.49
                           }
                       ]
                   }
               ]
            },
            {
               "FirstName": "Bob",
               "LastName": "Hanson",
               "ShipToState": "TX",
               "Orders": [
                   {
                       "Product": "Sailor",
                       "CreationDate": datetime.datetime(2013, 1, 1),
                       "ShippingTotal": 7.35,
                       "Items": [
                           {
                               "ProductName": "Koala",
                               "Quantity": 4,
                               "UnitPrice": 52.03
                           }
                       ]
                   },
                   {
                       "Product": "Koala",
                       "CreationDate": datetime.datetime(2013, 12, 1),
                       "ShippingTotal": 14.61,
                       "Items": [
                           {
                               "ProductName":  "Ninja",
                               "Quantity": 6,
                               "UnitPrice": 11.12
                           },
                           {
                               "ProductName": "Frog",
                               "Quantity": 1, 
                               "UnitPrice": 14.68
                           }
                       ]
                   }
               ] 
            },
            {
                "FirstName": "Alice",
                "LastName": "Wonderland",
                "ShipToState": "TX",
                "Orders": []
            }
        ]
    }