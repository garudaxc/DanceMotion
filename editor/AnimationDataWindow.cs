﻿using UnityEngine;
using System.Collections;
using UnityEditor;
using AnimationSerialize;
using System.IO;
using ProtoBuf;
using System.Collections.Generic;

public class AnimationDataWindow : EditorWindow {
	string myString = "Hello World";
	bool groupEnabled;
	bool myBool = true;
	float myFloat = 1.23f;


    static AnimationClip animation_;
    static GameObject animFig_;
	
	// Add menu named "My Window" to the Window menu
	[MenuItem ("MyMenu/My Window2")]
	static void Init () {
        // Get existing open window or if none, make a new one:
        AnimationDataWindow window = (AnimationDataWindow)EditorWindow.GetWindow (typeof (AnimationDataWindow));
		window.Show();
	}
	
	void OnGUI () {      
        		
		GUILayout.Label ("Base Settings", EditorStyles.boldLabel);
		myString = EditorGUILayout.TextField ("Text Field", myString);
		
		//groupEnabled = EditorGUILayout.BeginToggleGroup ("Optional Settings", groupEnabled);
		//myBool = EditorGUILayout.Toggle ("Toggle", myBool);
		//myFloat = EditorGUILayout.Slider ("Slider", myFloat, -3, 3);
        //EditorGUILayout.EndToggleGroup();

        animFig_ = (GameObject)EditorGUILayout.ObjectField(animFig_, typeof(GameObject));
        animation_ = (AnimationClip)EditorGUILayout.ObjectField(animation_, typeof(AnimationClip));


        if (GUILayout.Button("Extruct Feature")) {
            Debug.ClearDeveloperConsole();
            //CallExtractMotionFeature();
            ExtractingMotionFeatures();
        }

        //if (animation_ != null)
        //{
        //    LoadAnimationData();
        //}
	}

    void CallExtractMotionFeature() {
        if (animFig_ == null) {
            Debug.Log("please assign animation fig");
            return;
        }

        ExtractMotionFeatures extractor = animFig_.GetComponent<ExtractMotionFeatures>();
        extractor.ExtractFeatures();
    }

    CurveData.ChannelType GetChannelType(string name) {
        if (name == "m_LocalPosition.x") {
            return CurveData.ChannelType.Posx;
        } else if (name == "m_LocalPosition.y") {
            return CurveData.ChannelType.Posy;
        } else if (name == "m_LocalPosition.z") {
            return CurveData.ChannelType.Posz;
        } else if (name == "m_LocalRotation.x") {
            return CurveData.ChannelType.Rotx;
        } else if (name == "m_LocalRotation.y") {
            return CurveData.ChannelType.Roty;
        } else if (name == "m_LocalRotation.z") {
            return CurveData.ChannelType.Rotz;
        } else if (name == "m_LocalRotation.w") {
            return CurveData.ChannelType.Rotw;
        }

        throw new System.Exception("unknow animation channel");
    }

    void TranversCollectJoints_r(GameObject go, int parent, List<JointNode> list) {

        JointNode joint = new JointNode() {
            Name = go.name,
            Parent = parent
        };

        list.Add(joint);
        int index = list.Count - 1;

        for(int i = 0; i < go.transform.childCount; i++) {
            TranversCollectJoints_r(go.transform.GetChild(i).gameObject, index, list);
        }        
    }
    
    void LoadAnimationData() {
        if (animFig_ == null) {
            Debug.Log("please assign animation fig");
            return;
        }

        ClipData clipData = new ClipData();

        TranversCollectJoints_r(animFig_, -1, clipData.Joints);
        foreach(var j in clipData.Joints) {
            Debug.Log(j.Name);
        }
        
        var bindings = AnimationUtility.GetCurveBindings(animation_);
        for (int i = 0; i < bindings.Length; i++) {
            var binding = bindings[i];
            //Debug.Log(i + " " + binding.path + "$" + binding.propertyName);

            if (binding.propertyName == "m_LocalScale.x" ||
                binding.propertyName == "m_LocalScale.y" ||
                binding.propertyName == "m_LocalScale.z") {
                continue;
            }

            AnimationCurve curveFrom = AnimationUtility.GetEditorCurve(animation_, binding);
            CurveData curveTo = new CurveData {
                Path = binding.path,
                Channel = GetChannelType(binding.propertyName)
            };
            //Debug.Log("number of keys " + curveFrom.length);
            

            for (int j = 0; j < curveFrom.length; j++) {
                Keyframe frame = curveFrom.keys[j];
                CurveData.Key key = new CurveData.Key {
                    Time = frame.time,
                    Value = frame.value,
                    Tangent = frame.inTangent
                };

                //string key = string.Format("key: time {0} value {1} inTanget {2} outTanget{3}", frame.time, frame.value, frame.inTangent, frame.outTangent);
                //Debug.Log(key);
                curveTo.Datas.Add(key);
            }

            clipData.Curves.Add(curveTo);
        }

        Debug.Log("got curves " + clipData.Curves.Count);

        using (var file = File.Create("I:/clipData.bin")) {
            Serializer.Serialize(file, clipData);
        }
    }

    GameObject FindGameObjectByName_r(GameObject go, string name) {
        if (go.name.Equals(name)) {
            return go;
        }

        foreach(Transform child in go.transform) {
            var found = FindGameObjectByName_r(child.gameObject, name);
            if (found != null) {
                return found;
            }
        }

        return null;
    }

    void ExtractingMotionFeatures(Transform[] joints, Animation animation, Dictionary<string, float> musicInfo, string outputFile) {

        float bpm = musicInfo["bpm"];
        float enterTime = musicInfo["et"];

        // 一拍中分6个window，window间50%重叠，每个window采样6次
        // 一拍共6 * 3.5=21个采样点
        float beat = 60.0f / bpm;
        float dt = beat / 21.0f;
        Debug.LogFormat("bpm {0} delta time {1}", bpm, dt);
        
        Transform reference = joints[0];
        AnimationState state = animation["Take 001"];
        state.weight = 1.0f;
        state.enabled = true;

        //float dt = 0.01f;
        float invdt = 1.0f / dt;

        Quaternion[] prevRot = new Quaternion[joints.Length];
        // init rotation to first frame
        float startTime = enterTime + (dt / 2.0f);
        state.time = startTime;
        animation.Sample();
        for (int i = 0; i < joints.Length; i++) {
            prevRot[i] = joints[i].localRotation;
        }

        var featureData = new List<float>();
        int numSamples = (int)((state.length - enterTime) / dt);

        for (int i = 0; i < numSamples; i++) {
            float time = startTime + dt * i;
            state.time = time;
            animation.Sample();

            //featureData.Add(time);
            Vector3 refPos = reference.position;
            for (int j = 0; j < joints.Length; j++) {
                float dis = (joints[j].position - refPos).magnitude;
                Quaternion q = joints[j].localRotation;
                float omiga = Quaternion.Angle(q, prevRot[j]);
                prevRot[j] = q;

                featureData.Add(dis * invdt);
                featureData.Add(omiga * invdt);
            }
        }

        Debug.LogFormat("feature data {0} frames {1} joints {2} floats", numSamples, joints.Length, numSamples * joints.Length * 2);

        FileStream fs = new FileStream(outputFile, FileMode.Create, FileAccess.Write);
        BinaryWriter bw = new BinaryWriter(fs);

        bw.Write(numSamples);
        bw.Write(joints.Length * 2);
        bw.Write(startTime);
        bw.Write(dt);
        // sample per beat
        bw.Write(21);

        foreach (var d in featureData) {
            bw.Write(d);
        }

        bw.Close();
        fs.Close();

        Debug.LogFormat("write file {0}", outputFile);
    }

    Dictionary<string, float> LoadMusicInfo(string path) {
        string filename = Path.Combine(path, "info.txt");
        if (!File.Exists(filename)) {
            Debug.LogErrorFormat("can not find file {0}", filename);
            return null;
        }

        string[] lines = File.ReadAllLines(filename);

        Dictionary<string, float> dic = new Dictionary<string, float>();

        foreach(var l in lines) {
            string[] s = l.Split(new char[] { '=' });
            if (s != null) {
                float val = float.Parse(s[1]);
                dic.Add(s[0], val);
            }
        }

        return dic;
    }


    void ExtractingMotionFeatures() {
        
        //Quaternion[] q = new Quaternion[3];
        //Debug.LogFormat("quaternion : {0}", q[0].ToString());
        //return;

        //Based on these individual frames’ motion 
        //feature values, we can further extract each feature’s mean,
        //median, variance, and also the mean, median, and variance
        //of the feature’s first order forward finite difference.

        var select = Selection.activeObject;
        if (select.GetType() != typeof(GameObject)) {
            Debug.Log("please select a prefab");
            return;
        }

        GameObject fig = (GameObject)GameObject.Instantiate(select);
        Animation animation = fig.GetComponent<Animation>();
        if (animation == null) {
            Debug.LogError("not having animation component!");
            return;
        }

        string path = AssetDatabase.GetAssetPath(select);
        path = Path.GetDirectoryName(path);

        var musicInfo = LoadMusicInfo(path);

        path = Path.Combine(path, "motion_feature.bin");

        // find curve
        //// find node
        string[] jointName = new string[] {
            "Bip01 Pelvis",
            "Bip01 Spine",
            "Bip01 Neck",
            "Bip01 L Thigh",
            "Bip01 R Thigh",
            "Bip01 L Calf",
            "Bip01 R Calf",
            "Bip01 L Foot",
            "Bip01 R Foot",
            "Bip01 L UpperArm",
            "Bip01 R UpperArm",
            "Bip01 L Forearm",
            "Bip01 R Forearm",
        };

        Transform[] joints = new Transform[jointName.Length];

        for (int i = 0; i < jointName.Length; i++) {
            GameObject o = FindGameObjectByName_r(fig, jointName[i]);
            if (o == null) {
                Debug.LogFormat("can not found gameobject {0}", jointName[i]);
            } else {
                joints[i] = o.transform;
                //Debug.LogFormat("founed {0}", joints[i]);
            }
        }

        ExtractingMotionFeatures(joints, animation, musicInfo, path);
    }
}

