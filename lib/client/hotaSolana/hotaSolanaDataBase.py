class BaseElement:
    def __init__(self, key="", value=""):
        self.key = key
        self.value = value


def GenBaseEleList(object):
    data = []
    for key in object:
        data.append(BaseElement(key, object[key]))
    return data


class BaseStruct:
    def __init__(self, data=None):
        if data is None:
            data = []
        self.data = []
        if not isinstance(data, list):
            raise Exception("Error data is not list")
        for item in data:
            if isinstance(item, BaseElement):
                self.data.append(item)
            else:
                raise Exception("Error item is not BaseElement")
        self.data = data

        self.mapName2Data = dict()
        for item in self.data:
            self.mapName2Data[item.key] = item

    def get(self, key):
        if key in self.mapName2Data:
            return self.mapName2Data[key].value
        raise Exception("Error key not found")

    def set(self, key, value):
        if key in self.mapName2Data:
            self.mapName2Data[key].value = value
        else:
            raise Exception("Error key not found")

    def object2struct(self, object):
        for item in self.data:
            if isinstance(object[item.key], int) and isinstance(item.value, int):
                item.value = object[item.key]
            elif isinstance(object[item.key], dict) and isinstance(item.value, BaseStruct):
                item.value.object2struct(object[item.key])
            else:
                raise Exception("Error object is not match struct")

    def struct2object(self):
        object = {}
        for item in self.data:
            if isinstance(item.value, BaseStruct):
                object[item.key] = item.value.struct2object()
            else:
                object[item.key] = item.value
        return object

    def size(self):
        size = 0
        for item in self.data:
            if isinstance(item.value, BaseStruct):
                size += item.value.size()
            else:
                size += 1
        return size

    def deserialize(self, buffers, index=0, checkSize=True):
        if(checkSize and index == 0 and len(buffers) != self.size()):
            raise Exception(f"Error buffer size not match buffers:{len(buffers)} != self.size:{self.size()}")
        return self._deserialize(self.data, buffers, index)

    def serialize(self):
        return self._serialize(self.data)

    def _deserialize(self, dataStruct, buffers, index):
        for item in dataStruct:
            if isinstance(item.value, BaseStruct):
                index = item.value.deserialize(buffers, index, checkSize=False)
            elif isinstance(item.value, int):
                item.value = buffers[index]
                index += 1
            else:
                raise Exception("Error data struct is not number or struct")
        return index

    def _serialize(self, dataStruct):
        buffer = []
        for item in dataStruct:
            if isinstance(item.value, BaseStruct):
                buffer.extend(item.value.serialize())
            elif isinstance(item.value, int):
                buffer.append(item.value)
            else:
                raise Exception("Error data struct is not number or struct")
        return buffer

# Base data type

# Uint 8


class HotaUint8(BaseStruct):
    def __init__(self, inUint=0):
        super().__init__([BaseElement("value", inUint)])

    def value(self):
        return self.get("value")

    def setValue(self, inUint):
        self.set("value", inUint)

    def struct2object(self):
        return self.value()

    def object2struct(self, object):
        self.setValue(object)

# Array int data


class HotaArrayInt(BaseStruct):
    def __init__(self, lenArr, inArray=[], defaultData=0):
        data = []
        for i in range(lenArr):
            if i < len(inArray):
                data.append(BaseElement(i, inArray[i]))
            else:
                data.append(BaseElement(i, HotaUint8(defaultData)))
        super().__init__(data)

# Uint 16


class HotaUint16(BaseStruct):
    def __init__(self, inUint=0):
        inArray = [inUint & 0xff, (inUint >> 8) & 0xff]
        super().__init__([BaseElement("value", HotaArrayInt(2, inArray, 0))])

    def struct2object(self):
        return self.get("value").get(0) + self.get("value").get(1) * 256

    def object2struct(self, inUint):
        self.get("value").set(0, inUint & 0xff)
        self.get("value").set(1, (inUint >> 8) & 0xff)

# Uint 32


class HotaUint32(BaseStruct):
    def __init__(self, inUint=0):
        inArray = [
            inUint & 0xff,
            (inUint >> 8) & 0xff,
            (inUint >> 16) & 0xff,
            (inUint >> 24) & 0xff,
        ]
        super().__init__([BaseElement("value", HotaArrayInt(4, inArray, 0))])
        

    def struct2object(self):
        return (
            self.get("value").get(0)
            + self.get("value").get(1) * 256
            + self.get("value").get(2) * 256 * 256
            + self.get("value").get(3) * 256 * 256 * 256
        )

    def object2struct(self, inUint):
        self.get("value").set(0, inUint & 0xff)
        self.get("value").set(1, (inUint >> 8) & 0xff)
        self.get("value").set(2, (inUint >> 16) & 0xff)
        self.get("value").set(3, (inUint >> 24) & 0xff)

# Uint 64


class HotaUint64(BaseStruct):
    def __init__(self, inUint=0):
        inArray = [
            inUint & 0xff,
            (inUint >> 8) & 0xff,
            (inUint >> 16) & 0xff,
            (inUint >> 24) & 0xff,
            (inUint >> 32) & 0xff,
            (inUint >> 40) & 0xff,
            (inUint >> 48) & 0xff,
            (inUint >> 56) & 0xff,
        ]
        super().__init__([BaseElement("value", HotaArrayInt(8, inArray, 0))])

    def struct2object(self):
        return (
            self.get("value").get(0)
            + self.get("value").get(1) * 256
            + self.get("value").get(2) * 256 * 256
            + self.get("value").get(3) * 256 * 256 * 256
            + self.get("value").get(4) * 256 * 256 * 256 * 256
            + self.get("value").get(5) * 256 * 256 * 256 * 256 * 256
            + self.get("value").get(6) * 256 * 256 * 256 * 256 * 256 * 256
            + self.get("value").get(7) * 256 * 256 *
            256 * 256 * 256 * 256 * 256
        )

    def object2struct(self, inUint):
        self.get("value").set(0, inUint & 0xff)
        self.get("value").set(1, (inUint >> 8) & 0xff)
        self.get("value").set(2, (inUint >> 16) & 0xff)
        self.get("value").set(3, (inUint >> 24) & 0xff)
        self.get("value").set(4, (inUint >> 32) & 0xff)
        self.get("value").set(5, (inUint >> 40) & 0xff)
        self.get("value").set(6, (inUint >> 48) & 0xff)
        self.get("value").set(7, (inUint >> 56) & 0xff)

# Uint128
class HotaUint128(BaseStruct):
    def __init__(self, inUint=0):
        inArray = [
            ((inUint >> i*8) & 0xff) for i in range(16)
        ]
        super().__init__([BaseElement("value", HotaArrayInt(16, inArray, 0))])

    def struct2object(self):
        return sum([self.get("value").get(i) * (256 ** i) for i in range(16)])
    
    def object2struct(self, inUint):
        for i in range(16):
            self.get("value").set(i, (inUint >> i*8) & 0xff)

# UintX
class HotaUintX(BaseStruct):
    def __init__(self, lenArr, inUint=0):
        inArray = [
            (inUint >> i*8) & 0xff for i in range(lenArr)
        ]
        super().__init__([BaseElement("value", HotaArrayInt(lenArr, inArray, 0))])

    def struct2object(self):
        return sum([self.get("value").get(i) * (256 ** i) for i in range(len(self.get("value")))])
    
    def object2struct(self, inUint):
        for i in range(len(self.get("value"))):
            self.get("value").set(i, (inUint >> i*8) & 0xff)

# String 64bit data


class HotaString64(HotaArrayInt):
    def __init__(self, lenArr, inString=""):
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        inArray = []
        for i in range(len(inString)):
            if self.alphabet.find(inString[i]) == -1:
                raise Exception("Error string is not in alphabet")
                return
            inArray.append(self.alphabet.find(inString[i]) + 1)
        super().__init__(lenArr, inArray, 0)

    def toString(self):
        str = ""
        for i in range(len(self.data)):
            if self.data[i].value == 0:
                break
            str += self.alphabet[self.data[i].value - 1]
        return str

    def struct2object(self):
        return self.toString()

    def object2struct(self, object):
        for i in range(len(self.data)):
            self.data[i].value = 0
        for i in range(len(object)):
            self.data[i].value = self.alphabet.find(object[i]) + 1

# Array of struct


class HotaArrayStruct(BaseStruct):
    def __init__(self, lenArr, lamdaCreateObj, inArray=[]):
        if not callable(lamdaCreateObj):
            raise Exception("Error lamdaCreateObj is not function")
        if not isinstance(lamdaCreateObj(), BaseStruct):
            raise Exception("Error struct is not BaseStruct")
        data = []
        for i in range(lenArr):
            if i < len(inArray):
                data.append(BaseElement(i, inArray[i]))
            else:
                data.append(BaseElement(i, lamdaCreateObj()))
        super().__init__(data)

# Vector of struct


class HotaVectorStruct(BaseStruct):
    def __init__(self, maxlen, lamdaCreateObj, inArray=[], UintLen=HotaUint32(0)):
        if not callable(lamdaCreateObj):
            raise Exception("Error lamdaCreateObj is not function")
        if not isinstance(lamdaCreateObj(), BaseStruct):
            raise Exception("Error struct is not BaseStruct")
        data = []
        data.append(BaseElement("length", UintLen))
        data.append(BaseElement("data", HotaArrayStruct(
            maxlen, lamdaCreateObj, inArray)))
        super().__init__(data)

    def push(self, newObj):
        self.get("data").get(self.get("length").value()).object2struct(newObj)
        self.get("length").setValue(self.get("length").value() + 1)

    def pop(self):
        self.get("length").setValue(self.get("length").value() - 1)

    def remove(self, index):
        for i in range(index, self.data[0].value - 1):
            self.get("data").set(i, self.get("data").get(i + 1))
        self.get("length").setValue(self.get("length").value() - 1)

    def getByIndex(self, index):
        return self.get("data").get(index)

    def length(self):
        return self.data.get("length")

    def clear(self):
        self.get("length").setValue(0)

    def isEmpty(self):
        return self.get("length").value() == 0

# Hex data
class HotaHex(BaseStruct):
    def __init__(self, lenArr, inArray=[]):
        data = []
        for i in range(lenArr):
            if i < len(inArray):
                data.append(BaseElement(i, inArray[i]))
            else:
                data.append(BaseElement(i, HotaUint8(0)))
        super().__init__(data)

    def struct2object(self) -> str:
        # Convert to hex string
        hexStr = ""
        for i in range(len(self.data)):
            hexStr += hex(self.get(i).value())[2:].zfill(2)
        return hexStr

    def object2struct(self, hex: str) -> None:
        # Convert from hex to bytes
        for i in range(0, len(hex), 2):
            bytes = int(hex[i:i+2], 16)
            self.get(i//2).setValue(bytes)