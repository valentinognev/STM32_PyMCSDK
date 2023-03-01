cmake_minimum_required ( VERSION 2.8 )

project ( example C )

find_package ( LibFTDI1 NO_MODULE REQUIRED )
include ( ${LIBFTDI_USE_FILE} )

# find libusb
find_package( PkgConfig )
if (PkgConfig_FOUND)
  pkg_check_modules( LIBUSB libusb-1.0 )
  if (LIBUSB_FOUND)
    include_directories ( ${LIBUSB_INCLUDE_DIRS} )
  else()
    find_package ( USB1 REQUIRED )
    include_directories ( ${LIBUSB_INCLUDE_DIR} )
  endif()
endif()

add_executable ( example main.c spi_ft232.c)
target_link_libraries( example ${LIBFTDI_LIBRARIES} )

install ( TARGETS example
          DESTINATION bin )
          
