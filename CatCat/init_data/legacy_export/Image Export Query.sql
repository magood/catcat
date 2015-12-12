SELECT i.*, AsText(l.loc) loc_wkt
FROM catcat2.Image i
	join catcat2.Location l on i.loc_id=l.id