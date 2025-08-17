# author: haru233

from inc_noesis import *
import struct

def registerNoesisTypes():
    handle = noesis.register("Sleeping Dogs Model", ".bin")
    noesis.setHandlerTypeCheck(handle, checkType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def checkType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)

    
    ModelCount = 0
    IndexBuffers = {}
    VertexBuffers_1 = {}

    VertexBuffers_3 = {}
    ModelTableOffsets = []

    while bs.tell() < len(data):
        print("Starting LoadModel...")

        

        ChunkID = bs.readUInt()
        bs.seek(4, 1)
        ChunkSize = bs.readUInt()
        bs.seek(4, 1)

        curOffset = bs.tell()
        print("At offset " + str(curOffset) + ", ChunkID: " + str(ChunkID) + ", ChunkSize: " + str(ChunkSize))

        pos = bs.tell()      
        padding = (16 - (pos % 16)) % 16
        bs.seek(padding, 1)

        if ChunkID == 2056721529:
            # Save buffer ID and current stream position
            bs.seek(12, 1)
            bufferIDPos = bs.tell()
            BufferID = bs.readUInt()
            bs.seek(12, 1)
            BufferName = bs.readBytes(36)
            bs.seek(12, 1)
            Stride = bs.readUInt()

            
            if BufferID not in IndexBuffers and Stride == 2:
                IndexBuffers[BufferID] = bufferIDPos
                print("Added IndexBuffer ID " + str(BufferID) + " at pos " + str(bufferIDPos))

            elif BufferID not in VertexBuffers_1 and (Stride == 12 or Stride == 16 or Stride == 48):
                VertexBuffers_1[BufferID] = bufferIDPos
                print("Added VertexBuffer_1 ID " + str(BufferID) + " at pos " + str(bufferIDPos))

            elif BufferID not in VertexBuffers_3 and (Stride == 4 or Stride == 8 or Stride == 16):
                VertexBuffers_3[BufferID] = bufferIDPos
                print("Added VertexBuffer_3 ID " + str(BufferID) + " at pos " + str(bufferIDPos))

            bs.seek(curOffset + ChunkSize, 0)

            continue

        elif ChunkID == 1845060531:
            ModelCount += 1
            ModelTableOffsets.append(curOffset)
            bs.seek(curOffset + ChunkSize, 0)
            print("Found ModelTable chunk at offset " + str(curOffset) + " (ModelCount=" + str(ModelCount) + ")")

            continue

        elif ChunkID == 3925339657:
            bs.seek(curOffset + ChunkSize, 0)
            
            if bs.tell() < len(data):
                Read1 = bs.readUInt()
                Read2 = bs.readUInt()
                Read3 = bs.readUInt()
                Read4 = bs.readUInt()

                if Read2 + Read4 == Read3:
                    bs.seek(Read2, 1)
                    continue
                
                else:
                    bs.seek(-16, 1)
                    continue

            else:
                continue

        else:
            bs.seek(curOffset + ChunkSize, 0)

    print("IndexBuffers found: " + str(len(IndexBuffers)) + ", VertexBuffers_1 found: " + str(len(VertexBuffers_1)) + ", VertexBuffers_3 found: " + str(len(VertexBuffers_3)))
    print("Model tables found: " + str(len(ModelTableOffsets)))

        


    for ModelIndex, ModelTableOffset in enumerate(ModelTableOffsets):
        print("Processing model " + str(ModelIndex) + " at offset " + str(ModelTableOffset))

        meshList = []

        print(ModelTableOffset)
        bs.seek(ModelTableOffset, 0)
        print(bs.tell())
        
        bs.seek(28, 1)
        bs.seek(36, 1)
        bs.seek(60, 1)

        Read = bs.readBytes(68)
        MeshPrimitiveCount = Read[4]
        print("MeshPrimitiveCount: " + str(MeshPrimitiveCount))


        MeshPrimitiveOffsetList = bs.readBytes(MeshPrimitiveCount * 4) # Each offset is Relative to OffsetList start position
    
        pos = bs.tell()      
        padding = (16 - (pos % 16)) % 16
        bs.seek(padding, 1)

        
        MeshPrimitiveInfoList = []

        print("IndexBuffers:", IndexBuffers)
        print("VertexBuffers_1:", VertexBuffers_1)

        IndexBufferIDList = []
        VertexBuffer1_IDList = []

        VertexBuffer3_IDList = []       
        for i in range(MeshPrimitiveCount):
            

            bs.seek(44, 1)
            IndexBufferID = bs.readUInt()
            IndexBufferIDList.append(IndexBufferID)

            bs.seek(12, 1)
            VertexBuffer1_ID = bs.readUInt()
            VertexBuffer1_IDList.append(VertexBuffer1_ID)
            
            bs.seek(28, 1)
            VertexBuffer3_ID = bs.readUInt()
            bs.seek(20, 1)

            MeshPrimitiveOffsetInIndexBuffer = bs.readUInt() * 2
            TriangleCount = bs.readUInt()
            bs.seek(20, 1)

            print("MeshPrimitive {}: IndexBufferID={}, VertexBufferID={}, Offset={}, Triangles={}".format(
                i, IndexBufferID, VertexBuffer1_ID, MeshPrimitiveOffsetInIndexBuffer, TriangleCount))
            
            MeshPrimitiveInfoList.append({
                "IndexBufferID": IndexBufferID,
                "VertexBuffer1_ID": VertexBuffer1_ID,

                "VertexBuffer3_ID": VertexBuffer3_ID,
                "IndexOffset": MeshPrimitiveOffsetInIndexBuffer,
                "TriangleCount": TriangleCount
            })

        
        for i, MeshPrim in enumerate(MeshPrimitiveInfoList):

            Indices = []
            Positions = []
            Normals = []
            Tangents = []
            UVs0 = []
            UVs1 = []
            Colors = []

            indexBufferID = MeshPrim["IndexBufferID"]
            vertexBuffer1_ID = MeshPrim["VertexBuffer1_ID"]

            vertexBuffer3_ID = MeshPrim["VertexBuffer3_ID"]
            indexOffset = MeshPrim["IndexOffset"]
            triangleCount = MeshPrim["TriangleCount"]

            print(indexBufferID)
            print(vertexBuffer1_ID)
            print(indexOffset)
            print(triangleCount)

            # === Index buffer ===
            if indexBufferID not in IndexBuffers:
                print("Skipping this Mesh Primitive, it doesn't have Index Buffer Reference")
                print(indexBufferID)
                continue


            if indexBufferID in IndexBuffers:
                bs.seek(IndexBuffers[indexBufferID], 0)
                bs.seek(180, 1)
                StartOfIndexBuffer = bs.tell()
                print(StartOfIndexBuffer + indexOffset)

                print(" → Mesh {}: Reading {} indices from offset {}".format(i, triangleCount * 3, StartOfIndexBuffer + indexOffset))
                print(" → First 6 indices: {}".format(Indices[:6]))

                bs.seek(StartOfIndexBuffer + indexOffset, 0)
                for t in range(triangleCount * 3):
                  
                  Indices.append(bs.readUShort())

             
            # === Vertex Buffers ===
            if vertexBuffer1_ID in VertexBuffers_1:
                bs.seek(VertexBuffers_1[vertexBuffer1_ID], 0)
                bs.seek(64, 1)
                VertexStride = bs.readUInt()
                VertexCount = bs.readUInt()
                bs.seek(108, 1)

                for j in range(VertexCount):
                    if VertexStride == 16:
                        px = bs.readShort() / 32767.0
                        pz = bs.readShort() / 32767.0
                        py = bs.readShort() / 32767.0
                        pw = bs.readShort() / 32767.0

                        nx = bs.readUByte() / 255.0
                        nz = bs.readUByte() / 255.0
                        ny = bs.readUByte() / 255.0
                        nw = bs.readUByte() / 255.0

                        tx = bs.readUByte() / 255.0
                        tz = bs.readUByte() / 255.0
                        ty = bs.readUByte() / 255.0
                        tw = bs.readUByte() / 255.0

                        Positions.append(NoeVec3([px, pz, py]))
                        Normals.append(NoeVec3([nx, nz, ny]))
                        Tangents.append(NoeVec4([tx, tz, ty, tw]))

                    elif VertexStride == 12:
                        px = bs.readFloat()
                        pz = bs.readFloat()
                        py = bs.readFloat()

                     
                        Positions.append(NoeVec3([px, pz, py]))
                    
                    elif VertexStride == 48:
                        px = bs.readFloat()
                        pz = bs.readFloat()
                        py = bs.readFloat()

                        U0 = bs.readHalfFloat()
                        V0 = bs.readHalfFloat()

                        U1 = bs.readHalfFloat()
                        V1 = bs.readHalfFloat()

                        nx = bs.readFloat()
                        nz = bs.readFloat()
                        ny = bs.readFloat()
                     

                        tx = bs.readFloat()
                        tz = bs.readFloat()
                        ty = bs.readFloat()
                        
                        color1 = bs.readUbyte() / 255.0
                        color2 = bs.readUbyte() / 255.0
                        color3 = bs.readUbyte() / 255.0

                        Positions.append(NoeVec3([px, pz, py]))
                        UVs0.append(NoeVec3([U0, V0, 0.0]))
                        UVs1.append(NoeVec3([U1, V1, 0.0]))
                        Normals.append(NoeVec3([nx, nz, ny]))
                        Tangents.append(NoeVec4([tx, tz, ty, 0.0]))
                        Colors.append(NoeVec3([color1, color2, color3]))


                        

            if vertexBuffer3_ID in VertexBuffers_3:
                bs.seek(VertexBuffers_3[vertexBuffer3_ID], 0)
                bs.seek(64, 1)
                VertexStride = bs.readUInt()
                VertexCount = bs.readUInt()
                bs.seek(108, 1)

                for j in range(VertexCount):
                    if VertexStride == 4:
                        U = bs.readHalfFloat()
                        V = bs.readHalfFloat()

                        
                        UVs0.append(NoeVec3([U, V, 0.0]))

                    elif VertexStride == 8:
                        U = bs.readHalfFloat()
                        V = bs.readHalfFloat()

                        nx = bs.readUByte() / 255.0
                        nz = bs.readUByte() / 255.0
                        ny = bs.readUByte() / 255.0
                        nw = bs.readUByte() / 255.0

                        UVs0.append(NoeVec3([U, V, 0.0]))
                        Normals.append(NoeVec3([nx, nz, ny]))
                    
                    
                    elif VertexStride == 16:
                        U = bs.readHalfFloat()
                        V = bs.readHalfFloat()

                        nx = bs.readUByte() / 255.0
                        nz = bs.readUByte() / 255.0
                        ny = bs.readUByte() / 255.0
                        nw = bs.readUByte() / 255.0
                        
                        tx = bs.readUByte() / 255.0
                        tz = bs.readUByte() / 255.0
                        ty = bs.readUByte() / 255.0
                        tw = bs.readUByte() / 255.0

                        color1 = bs.readUbyte() / 255.0
                        color2 = bs.readUbyte() / 255.0
                        color3 = bs.readUbyte() / 255.0
                        color4 = bs.readUbyte() / 255.0

                      
                        UVs0.append(NoeVec3([U, V, 0.0]))
                        Normals.append(NoeVec3([nx, nz, ny]))
                        Tangents.append(NoeVec4([tx, tz, ty, tw]))
                        Colors.append(NoeVec4([color1, color2, color3, color4]))

            # === Build mesh ===

            mesh = NoeMesh(Indices, Positions, "mesh_{}_{}".format(ModelIndex, i))
            mesh.setNormals(Normals)
            mesh.setUVs(UVs0)
            if UVs1:
                mesh.setUVs(UVs1)
            meshList.append(mesh)

            
        if meshList:
            mdlList.append(NoeModel(meshList))
        else:
            print("⚠ No valid meshes found; skipping model append.")


        
        
        print("LoadModel finished successfully.")



    return 1

    