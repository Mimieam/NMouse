import datetime

def isValid(d, patterns):
	for p in patterns:
		try:
			return datetime.datetime.strptime(d, p).date().strftime("%Y%m%d")
		except :
			pass

def change_date_format(dates):
	_dates = [ d for d in dates if (d.count('/') or d.count('-')) == 2]
	patterns = ["%Y/%m/%d", "%d/%m/%Y", "%m-%d-%Y"]
	return [ _d for _d in [isValid(d,patterns) for d in dates] if _d]

dates = change_date_format(["2010/03/30", "15/12/2016", "11-15-2012", "11-45/2012", "20130720"])
print(*dates, sep='\n')


# import json

# def sort_by_price_ascending(json_string):
# 	obj = json.loads(json_string)
# 	obj.sort(key=lambda x: (x["price"], x["name"]))
# 	return json.dumps(obj)

# print(sort_by_price_ascending('[{"name":"coffee","price":9.99},{"name":"zggs","price":1},{"name":"eggs","price":1},{"name":"rice","price":4.04}]'))
# # print(sort_by_price_ascending('[{"name":"eggs","price":1},{"name":"coffee","price":9.99},{"name":"rice","price":4.04}]'))