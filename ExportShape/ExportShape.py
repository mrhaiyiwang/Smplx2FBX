"""
   Copyright (C) 2017 Autodesk, Inc.
   All rights reserved.

   Use of this software is subject to the terms of the Autodesk license agreement
   provided at the time of installation or download, or which otherwise accompanies
   this software in either electronic or hard copy form.

"""

import sys
sys.path.append(r'D:\Tools\FBX\2020.2\lib\Python37_x64')

from FbxCommon import *
from fbx import *
import json
import math

SAMPLE_FILENAME = "ExportShape.fbx"
JointsSize = 1 / 3
SkeletonWeights = []
nodeDict = {}
Num2Joints = {5: 'R_Calf', 8: 'R_Foot', 22: 'Jaw', 23: 'L_Eye', 6: 'Spine1', 18: 'L_ForeArm', 9: 'Spine2',
              1: 'L_Thigh', 52: 'R_Thumb1', 54: 'R_Thumb3', 53: 'R_Thumb2', 12: 'Neck', 21: 'R_Hand', 15: 'Head',
              24: 'R_Eye', 35: 'L_Ring2', 34: 'L_Ring1', 20: 'L_Hand', 16: 'L_UpperArm', 39: 'L_Thumb3', 38: 'L_Thumb2',
              37: 'L_Thumb1', 50: 'R_Ring2', 51: 'R_Ring3', 49: 'R_Ring1', 27: 'L_Index3', 26: 'L_Index2',
              25: 'L_Index1', 46: 'R_Pinky1', 17: 'R_UpperArm', 31: 'L_Pinky1', 3: 'Spine', 14: 'R_Shoulder',
              42: 'R_Index3', 41: 'R_Index2', 36: 'L_Ring3', 40: 'R_Index1', 19: 'R_ForeArm', 10: 'L_Toes',
              45: 'R_Middle3', 44: 'R_Middle2', 43: 'R_Middle1', 7: 'L_Foot', 32: 'L_Pinky2', 33: 'L_Pinky3',
              28: 'L_Middle1', 30: 'L_Middle3', 29: 'L_Middle2', 47: 'R_Pinky2', 0: 'Root', 48: 'R_Pinky3',
              2: 'R_Thigh', 13: 'L_Shoulder', 4: 'L_Calf', 11: 'R_Toes'}

Joints2Num = {'R_Calf': 5, 'R_Foot': 8, 'Jaw': 22, 'L_Eye': 23, 'Spine1': 6, 'L_ForeArm': 18, 'Spine2': 9, 'L_Thigh': 1,
              'R_Thumb1': 52, 'R_Thumb3': 54, 'R_Thumb2': 53, 'Neck': 12, 'R_Hand': 21, 'Head': 15, 'R_Eye': 24,
              'L_Ring2': 35, 'L_Ring1': 34, 'L_Hand': 20, 'L_UpperArm': 16, 'L_Thumb3': 39, 'L_Thumb2': 38,
              'L_Thumb1': 37, 'R_Ring2': 50, 'R_Ring3': 51, 'R_Ring1': 49, 'L_Index3': 27, 'L_Index2': 26,
              'L_Index1': 25, 'R_Pinky1': 46, 'R_UpperArm': 17, 'L_Pinky1': 31, 'Spine': 3, 'R_Shoulder': 14,
              'R_Index3': 42, 'R_Index2': 41, 'L_Ring3': 36, 'R_Index1': 40, 'R_ForeArm': 19, 'L_Toes': 10,
              'R_Middle3': 45, 'R_Middle2': 44, 'R_Middle1': 43, 'L_Foot': 7, 'L_Pinky2': 32, 'L_Pinky3': 33,
              'L_Middle1': 28, 'L_Middle3': 30, 'L_Middle2': 29, 'R_Pinky2': 47, 'Root': 0, 'R_Pinky3': 48,
              'R_Thigh': 2, 'L_Shoulder': 13, 'L_Calf': 4, 'R_Toes': 11}


def CreateScene(pSdkManager, pScene):
    # Create scene info
    lSceneInfo = FbxDocumentInfo.Create(pSdkManager, "SceneInfo")
    lSceneInfo.mTitle = "SMPL-X"
    lSceneInfo.mSubject = "SMPL-X model with weighted skin"
    lSceneInfo.mAuthor = "ExportScene01.exe sample program."
    lSceneInfo.mRevision = "rev. 1.0"
    lSceneInfo.mKeywords = "weighted skin"
    lSceneInfo.mComment = "no particular comments required."
    pScene.SetSceneInfo(lSceneInfo)

    lMeshNode = FbxNode.Create(pScene, "meshNode")
    smplxMaleMesh = CreateMesh(pSdkManager, "Mesh")
    lControlPoints = smplxMaleMesh.GetControlPoints()
    lMeshNode.SetNodeAttribute(smplxMaleMesh)
    lSkeletonRoot = CreateSkeleton(pSdkManager, "Skeleton")

    pScene.GetRootNode().AddChild(lMeshNode)
    pScene.GetRootNode().AddChild(lSkeletonRoot)

    weightsInfo = open("SkinWeights.txt", "r")
    for i in range(0, 55):
        SkeletonWeights.append(weightsInfo.readline())
    lSkin = FbxSkin.Create(pSdkManager, "")
    LinkMeshToSkeleton(lSdkManager, lMeshNode, lSkin)
    AddShape(pScene, lMeshNode)
    AnimateSkeleton(pSdkManager, pScene, lSkeletonRoot)


def AddShape(pScene, node):
    lBlendShape = FbxBlendShape.Create(pScene, "BlendShapes")

    shapeInfo = open("vertexLoc.txt", "r")
    for j in range(0, 1):
        lBlendShapeChannel = FbxBlendShapeChannel.Create(pScene, "ShapeChannel"+str(j))
        lShape = FbxShape.Create(pScene, "Shape"+str(j))
        lShape.InitControlPoints(10475)
        for i in range(0, 10475):
            ctrlPInfo = shapeInfo.readline().split(" ")
            lShape.SetControlPointAt(FbxVector4(0, 0, 0), i)
        lBlendShapeChannel.AddTargetShape(lShape)
        lBlendShape.AddBlendShapeChannel(lBlendShapeChannel)
    node.GetMesh().AddDeformer(lBlendShape)


# Create a cylinder centered on the Z axis.
def CreateMesh(pSdkManager, pName):
    # preparation
    lMesh = FbxMesh.Create(pSdkManager, pName)
    lMesh.InitControlPoints(10475)
    lControlPoints = lMesh.GetControlPoints()
    vertexLocList = []
    # read
    geoInfo = open("ImprovedGeometryInfo.txt", "r")

    for i in range(0, 10475):
        vertexInput = geoInfo.readline().split(' ')
        locX = vertexInput[0]
        locY = vertexInput[1]
        locZ = vertexInput[2]
        vertexLoc = FbxVector4(float(locX), float(locY), float(locZ))
        vertexLocList.append(vertexLoc)
        lControlPoints[i] = vertexLoc
    j = 0
    for i in range(0, 20908):
        fragmentInput = geoInfo.readline().split(' ')
        fragIndex1 = int(fragmentInput[0]) - 1
        fragIndex2 = int(fragmentInput[1]) - 1
        fragIndex3 = int(fragmentInput[2]) - 1
        lMesh.BeginPolygon(i)  # Material index.
        lMesh.AddPolygon(fragIndex1)
        lMesh.AddPolygon(fragIndex2)
        lMesh.AddPolygon(fragIndex3)
        # Control point index.
        lMesh.EndPolygon()
    for i in range(0, 10475):
        lMesh.SetControlPointAt(lControlPoints[i], i)
    return lMesh


# create 55 skeletons for SMPL-X model
def CreateSkeleton(pSdkManager, pName):
    # 2021.4.8 shape influence are not supported now
    # read
    jointsLoc = open("AdjustedJointsLoc.txt", "r")

    lSkeletonRootAttribute = FbxSkeleton.Create(lSdkManager, "Root")
    lSkeletonRootAttribute.SetSkeletonType(FbxSkeleton.eLimbNode)
    lSkeletonRootAttribute.Size.Set(JointsSize)
    lSkeletonRoot = FbxNode.Create(lSdkManager, "Root")
    lSkeletonRoot.SetNodeAttribute(lSkeletonRootAttribute)
    rootInfo = jointsLoc.readline().split(" ")
    lSkeletonRoot.LclTranslation.Set(FbxDouble3(float(rootInfo[1]), float(rootInfo[2]), float(rootInfo[3])))

    nodeDict[0] = lSkeletonRoot
    locDict = {0: (float(rootInfo[1]), float(rootInfo[2]), float(rootInfo[3]))}

    for i in range(1, 55):
        skeletonInfo = jointsLoc.readline().split(" ")
        skeletonName = Num2Joints[i]
        skeletonAtrribute = FbxSkeleton.Create(lSdkManager, skeletonName)
        skeletonAtrribute.SetSkeletonType(FbxSkeleton.eLimbNode)
        skeletonAtrribute.Size.Set(JointsSize)
        skeletonNode = FbxNode.Create(lSdkManager, skeletonName)
        skeletonNode.SetNodeAttribute(skeletonAtrribute)
        nodeDict[i] = skeletonNode
        locDict[i] = (float(skeletonInfo[1]), float(skeletonInfo[2]), float(skeletonInfo[3]))
        skeletonFather = int(skeletonInfo[0])
        fatherNode = nodeDict[skeletonFather]
        skeletonNode.LclTranslation.Set(FbxDouble3(float(float(skeletonInfo[1]) - float(locDict[skeletonFather][0])),
                                                   float(float(skeletonInfo[2]) - float(locDict[skeletonFather][1])),
                                                   float(float(skeletonInfo[3]) - float(locDict[skeletonFather][2]))))
        fatherNode.AddChild(skeletonNode)

    return lSkeletonRoot


def LinkMeshToSkeleton(pSdkManager, pMeshNode, lSkin):
    for i in range(0, 55):
        skeletonNode = nodeDict[i]
        skeletonName = skeletonNode.GetName()
        skeletonNum = Joints2Num[str(skeletonName)]
        skeletonWeightsInfo = SkeletonWeights[skeletonNum].split(' ')
        skeletonCluster = FbxCluster.Create(pSdkManager, "")
        skeletonCluster.SetLink(skeletonNode)
        skeletonCluster.SetLinkMode(FbxCluster.eNormalize)
        for j in range(0, 10475):
            skeletonCluster.AddControlPointIndex(j, float(skeletonWeightsInfo[j]))

        # Now we have the Mesh and the skeleton correctly positioned,
        # set the Transform and TransformLink matrix accordingly.
        lXMatrix = FbxAMatrix()
        lScene = pMeshNode.GetScene()
        if lScene:
            lXMatrix = lScene.GetAnimationEvaluator().GetNodeGlobalTransform(pMeshNode)
        skeletonCluster.SetTransformMatrix(lXMatrix)
        lScene = skeletonNode.GetScene()
        if lScene:
            lXMatrix = lScene.GetAnimationEvaluator().GetNodeGlobalTransform(skeletonNode)
        skeletonCluster.SetTransformLinkMatrix(lXMatrix)
        # Add the clusters to the Mesh by creating a skin and adding those clusters to that skin.
        # After add that skin.
        lSkin.AddCluster(skeletonCluster)

    pMeshNode.GetNodeAttribute().AddDeformer(lSkin)


def AnimateSkeleton(pSdkManager, pScene, pSkeletonRoot):
    with open("JointsSequence.json", mode="r", encoding="utf-8") as fp:
        jointsSequence = json.load(fp)
    lTime = FbxTime()
    lKeyIndex = 0
    lRoot = pSkeletonRoot
    # First animation stack.
    lAnimStackName = "json generated Animation"
    lAnimStack = FbxAnimStack.Create(pScene, lAnimStackName)

    # The animation nodes can only exist on AnimLayers therefore it is mandatory to
    # add at least one AnimLayer to the AnimStack. And for the purpose of this example,
    # one layer is all we need.
    lAnimLayer = FbxAnimLayer.Create(pScene, "Base Layer")
    lAnimStack.AddMember(lAnimLayer)

    fps = 25

    # Read Rot info from Json
    for i in range(len(jointsSequence)):
        # body pose
        for j in range(1, 22):
            skeletonNode = nodeDict[j]
            lCurveX = skeletonNode.LclRotation.GetCurve(lAnimLayer, "X", True)
            lCurveY = skeletonNode.LclRotation.GetCurve(lAnimLayer, "Y", True)
            lCurveZ = skeletonNode.LclRotation.GetCurve(lAnimLayer, "Z", True)
            lTime.SetSecondDouble(i / fps)
            if lCurveX:
                lCurveX.KeyModifyBegin()
                lKeyIndex = lCurveX.KeyAdd(lTime)[0]
                lCurveX.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["body_pose"][3*(j-1)]))
                lCurveX.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveX.KeyModifyEnd()
            if lCurveY:
                lCurveY.KeyModifyBegin()
                lKeyIndex = lCurveY.KeyAdd(lTime)[0]
                lCurveY.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["body_pose"][3*(j-1)+1]))
                lCurveY.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveY.KeyModifyEnd()
            if lCurveZ:
                lCurveZ.KeyModifyBegin()
                lKeyIndex = lCurveZ.KeyAdd(lTime)[0]
                lCurveZ.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["body_pose"][3*(j-1)+2]))
                lCurveZ.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveZ.KeyModifyEnd()
        # l hand
        for j in range(25, 40):
            skeletonNode = nodeDict[j]
            lCurveX = skeletonNode.LclRotation.GetCurve(lAnimLayer, "X", True)
            lCurveY = skeletonNode.LclRotation.GetCurve(lAnimLayer, "Y", True)
            lCurveZ = skeletonNode.LclRotation.GetCurve(lAnimLayer, "Z", True)
            lTime.SetSecondDouble(i / fps)
            if lCurveX:
                lCurveX.KeyModifyBegin()
                lKeyIndex = lCurveX.KeyAdd(lTime)[0]
                lCurveX.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["left_hand_pose"][3 * (j - 25)]))
                lCurveX.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveX.KeyModifyEnd()
            if lCurveY:
                lCurveY.KeyModifyBegin()
                lKeyIndex = lCurveY.KeyAdd(lTime)[0]
                lCurveY.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["left_hand_pose"][3 * (j - 25) + 1]))
                lCurveY.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveY.KeyModifyEnd()
            if lCurveZ:
                lCurveZ.KeyModifyBegin()
                lKeyIndex = lCurveZ.KeyAdd(lTime)[0]
                lCurveZ.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["left_hand_pose"][3 * (j - 25) + 2]))
                lCurveZ.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveZ.KeyModifyEnd()
        # r hand
        for j in range(40, 55):
            skeletonNode = nodeDict[j]
            lCurveX = skeletonNode.LclRotation.GetCurve(lAnimLayer, "X", True)
            lCurveY = skeletonNode.LclRotation.GetCurve(lAnimLayer, "Y", True)
            lCurveZ = skeletonNode.LclRotation.GetCurve(lAnimLayer, "Z", True)
            lTime.SetSecondDouble(i / fps)
            if lCurveX:
                lCurveX.KeyModifyBegin()
                lKeyIndex = lCurveX.KeyAdd(lTime)[0]
                lCurveX.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["right_hand_pose"][3 * (j - 40)]))
                lCurveX.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveX.KeyModifyEnd()
            if lCurveY:
                lCurveY.KeyModifyBegin()
                lKeyIndex = lCurveY.KeyAdd(lTime)[0]
                lCurveY.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["right_hand_pose"][3 * (j - 40) + 1]))
                lCurveY.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveY.KeyModifyEnd()
            if lCurveZ:
                lCurveZ.KeyModifyBegin()
                lKeyIndex = lCurveZ.KeyAdd(lTime)[0]
                lCurveZ.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["right_hand_pose"][3 * (j - 40) + 2]))
                lCurveZ.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
                lCurveZ.KeyModifyEnd()
        # jaw
        jawNode = nodeDict[22]
        lCurveX = jawNode.LclRotation.GetCurve(lAnimLayer, "X", True)
        lCurveY = jawNode.LclRotation.GetCurve(lAnimLayer, "Y", True)
        lCurveZ = jawNode.LclRotation.GetCurve(lAnimLayer, "Z", True)
        lTime.SetSecondDouble(i / fps)
        if lCurveX:
            lCurveX.KeyModifyBegin()
            lKeyIndex = lCurveX.KeyAdd(lTime)[0]
            lCurveX.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["jaw_pose"][0]))
            lCurveX.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveX.KeyModifyEnd()
        if lCurveY:
            lCurveY.KeyModifyBegin()
            lKeyIndex = lCurveY.KeyAdd(lTime)[0]
            lCurveY.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["jaw_pose"][1]))
            lCurveY.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveY.KeyModifyEnd()
        if lCurveZ:
            lCurveZ.KeyModifyBegin()
            lKeyIndex = lCurveZ.KeyAdd(lTime)[0]
            lCurveZ.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["jaw_pose"][2]))
            lCurveZ.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveZ.KeyModifyEnd()
        # l_eye
        lEyeNode = nodeDict[23]
        lCurveX = lEyeNode.LclRotation.GetCurve(lAnimLayer, "X", True)
        lCurveY = lEyeNode.LclRotation.GetCurve(lAnimLayer, "Y", True)
        lCurveZ = lEyeNode.LclRotation.GetCurve(lAnimLayer, "Z", True)
        lTime.SetSecondDouble(i / fps)
        if lCurveX:
            lCurveX.KeyModifyBegin()
            lKeyIndex = lCurveX.KeyAdd(lTime)[0]
            lCurveX.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["leye_pose"][0]))
            lCurveX.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveX.KeyModifyEnd()
        if lCurveY:
            lCurveY.KeyModifyBegin()
            lKeyIndex = lCurveY.KeyAdd(lTime)[0]
            lCurveY.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["leye_pose"][1]))
            lCurveY.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveY.KeyModifyEnd()
        if lCurveZ:
            lCurveZ.KeyModifyBegin()
            lKeyIndex = lCurveZ.KeyAdd(lTime)[0]
            lCurveZ.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["leye_pose"][2]))
            lCurveZ.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveZ.KeyModifyEnd()
        # r eye
        rEyeNode = nodeDict[24]
        lCurveX = rEyeNode.LclRotation.GetCurve(lAnimLayer, "X", True)
        lCurveY = rEyeNode.LclRotation.GetCurve(lAnimLayer, "Y", True)
        lCurveZ = rEyeNode.LclRotation.GetCurve(lAnimLayer, "Z", True)
        lTime.SetSecondDouble(i / fps)
        if lCurveX:
            lCurveX.KeyModifyBegin()
            lKeyIndex = lCurveX.KeyAdd(lTime)[0]
            lCurveX.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["reye_pose"][0]))
            lCurveX.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveX.KeyModifyEnd()
        if lCurveY:
            lCurveY.KeyModifyBegin()
            lKeyIndex = lCurveY.KeyAdd(lTime)[0]
            lCurveY.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["reye_pose"][1]))
            lCurveY.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveY.KeyModifyEnd()
        if lCurveZ:
            lCurveZ.KeyModifyBegin()
            lKeyIndex = lCurveZ.KeyAdd(lTime)[0]
            lCurveZ.KeySetValue(lKeyIndex, math.degrees(jointsSequence[str(i)]["reye_pose"][2]))
            lCurveZ.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
            lCurveZ.KeyModifyEnd()


if __name__ == "__main__":
    try:
        import FbxCommon
        from fbx import *
    except ImportError:
        print("Error: module FbxCommon and/or fbx failed to import.\n")
        print(
            "Copy the files located in the compatible sub-folder lib/python<version> into your python interpreter site-packages folder.")
        import platform

        if platform.system() == 'Windows' or platform.system() == 'Microsoft':
            print('For example: copy ..\\..\\lib\\Python27_x64\\* C:\\Python27\\Lib\\site-packages')
        elif platform.system() == 'Linux':
            print('For example: cp ../../lib/Python27_x64/* /usr/local/lib/python2.7/site-packages')
        elif platform.system() == 'Darwin':
            print(
                'For example: cp ../../lib/Python27_x64/* /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')
        sys.exit(1)

    # Prepare the FBX SDK.
    (lSdkManager, lScene) = FbxCommon.InitializeSdkObjects()

    # Create the scene.
    lResult = CreateScene(lSdkManager, lScene)

    if lResult == False:
        print("\n\nAn error occurred while creating the scene...\n")
        lSdkManager.Destroy()
        sys.exit(1)

    lSdkManager.GetIOSettings().SetBoolProp(EXP_FBX_EMBEDDED, True)
    lFileFormat = lSdkManager.GetIOPluginRegistry().GetNativeWriterFormat()

    # Save the scene.
    # The example can take an output file name as an argument.
    if len(sys.argv) > 1:
        lResult = FbxCommon.SaveScene(lSdkManager, lScene, sys.argv[1])
    # A default output file name is given otherwise.
    else:
        lResult = FbxCommon.SaveScene(lSdkManager, lScene, SAMPLE_FILENAME)

    if lResult == False:
        print("\n\nAn error occurred while saving the scene...\n")
        lSdkManager.Destroy()
        sys.exit(1)

    # Destroy all objects created by the FBX SDK.
    lSdkManager.Destroy()

    sys.exit(0)
