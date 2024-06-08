CC:= g++

CFLAGS:= -Wall -std=c++11

CFLAGS+= -shared -fPIC

CFLAGS+= -I/opt/nvidia/deepstream/deepstream-6.2/sources/includes/
CFLAGS+= -I/usr/local/cuda-11/targets/x86_64-linux/include/

LIBS:= -lnvinfer -lnvparsers
LFLAGS:= -Wl,--start-group $(LIBS) -Wl,--end-group

SRCFILES:= nvdsinfer_custombboxparser.cpp
TARGET_LIB:= libnvds_infercustomparser.so

all: $(TARGET_LIB)

$(TARGET_LIB) : $(SRCFILES)
	$(CC) -o $@ $^ $(CFLAGS) $(LFLAGS)

clean:
	rm -rf $(TARGET_LIB)