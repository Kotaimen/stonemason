# Stonemason

**Stonemason** is a complete rewrite of the unpopular [mason](https://github.com/Kotaimen/mason) tile map toolkit.  

Similar solutions:
- [TileScache](http://tilestache.org)
- [TileCache](http://tilecache.org)
- [Windshaft](https://github.com/CartoDB/Windshaft) 


## Features (planned)

- Tile map service
- Render pipeline
- Mass tile storage
- Debug and design server
- [mapnik](http://mapnik.org) as raster render engine 
- Homebrew high quality DEM terrain relief renderer
- Supports both zero configuration and distributed deployment


## Dependencies

- Python2>=2.7
- Python3>=3.3 (Geospatial related modules only supports py27)
- flask>=0.9
- pillow>=2.3
- numpy>=1.9, scipy>=0.10.0 (Optional)
- mapnik>=2.2 (Optional)
- geos>=3.3, gdal>=1.10 (Optional)
- imagemagick>=6.0 (Optional)
- PostgreSQL>=9.1, PostGIS>=2.1 (Optional)
- redis>=2.8 (Optional)
- memcached>=1.4
