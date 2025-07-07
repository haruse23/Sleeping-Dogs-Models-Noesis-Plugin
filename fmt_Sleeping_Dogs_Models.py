# author: haru233

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Sleeping Dogs Model", ".bin")
    noesis.setHandlerTypeCheck(handle, checkType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def checkType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)

    Indices = []
    Vertices = []
    Normals = []
    UVs = []

    while bs.tell() < len(data):
        print(bs.tell())
        ChunkID = bs.readUInt()
        bs.seek(4, 1)
        ChunkSize = bs.readUInt()
        bs.seek(4, 1)

        print(ChunkID)
        print(ChunkSize)

        if ChunkID != 2056721529:
            bs.read(ChunkSize)
            continue

        else:
            # First comes Index Buffer
            curOffset = bs.tell()
            padding = (16 - (curOffset % 16)) % 16
            bs.seek(padding, 1)

            bs.seek(68, 1)
            IndexBufferSize = bs.readUInt()
            bs.seek(8, 1)
            IndexCount = bs.readUInt() # IndexBufferSize // 2
            print(IndexCount)
            bs.seek(108, 1)
            for i in range(IndexCount):
                Index = bs.readUShort()
                Indices.append(Index)
            
            # Second comes Vertex Buffer
            # No reading chunk header here, (already read at the start of the loop till Index Buffer)
            curOffset = bs.tell()
            padding = (16 - (curOffset % 16)) % 16
            bs.seek(padding, 1)

            bs.seek(84, 1)
            VertexBufferSize = bs.readUInt()
            bs.seek(8, 1)
            VertexCount = bs.readUInt()
            bs.seek(108, 1)
            VertexStride = VertexBufferSize // VertexCount
            for i in range(VertexCount):
                positionX = bs.readShort() / 32767
                positionZ = bs.readShort() / 32767
                positionY = bs.readShort() / 32767
                positionW = bs.readShort() / 32767
              
                normalX = bs.readUByte() / 255
                normalZ = bs.readUByte() / 255
                normalY = bs.readUByte() / 255
                normalW = bs.readUByte() / 255
                
                bs.seek(VertexStride-12, 1)
                Vertices.append(NoeVec3([positionX, positionZ, positionY]))
                Normals.append(NoeVec3([normalX, normalZ, normalY]))

            curOffset = bs.tell()
            padding = (16 - (curOffset % 16)) % 16
            bs.seek(padding, 1)

            bs.seek(8, 1)
            ChunkSize2 = bs.readUInt()
            bs.seek(ChunkSize2 + 4, 1)
            bs.seek(84, 1)

            UVBufferSize = bs.readUInt()
            bs.seek(8, 1)
            UVCount = bs.readUInt() # must equal Vertex Count
            print(UVCount)

            bs.seek(108, 1)
            print(bs.tell())
            for i in range(UVCount):
                U = bs.readHalfFloat()
                V = bs.readHalfFloat()

                UVs.append(NoeVec3([U, V, 0.0]))
            print(bs.tell)
            break

        
    for i in range(5):
        print("UV: {} ({:.4f}, {:.4f})".format(i, UVs[i][0], UVs[i][1]))

    mesh = NoeMesh(Indices, Vertices, "mesh0")
    mesh.setNormals(Normals)
    mesh.setUVs(UVs)

    TextureName = "Sandra.png"
    Material = NoeMaterial("mymaterial", TextureName)
    mesh.setMaterial("mymaterial")

    model = NoeModel([mesh])
    model.setModelMaterials(NoeModelMaterials([], [Material]))
    
    mdlList.append(model)

    return 1

    