using UnityEngine;
using System.Collections;
using UnityEditor;
using AnimationSerialize;
using System.IO;
using ProtoBuf;
using System.Collections.Generic;

public class AnimationData : EditorWindow {
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
		AnimationData window = (AnimationData)EditorWindow.GetWindow (typeof (AnimationData));
		window.Show();
	}
	
	void OnGUI () {      
        		
		GUILayout.Label ("Base Settings", EditorStyles.boldLabel);
		myString = EditorGUILayout.TextField ("Text Field", myString);
		
		groupEnabled = EditorGUILayout.BeginToggleGroup ("Optional Settings", groupEnabled);
		myBool = EditorGUILayout.Toggle ("Toggle", myBool);
		myFloat = EditorGUILayout.Slider ("Slider", myFloat, -3, 3);

        EditorGUILayout.EndToggleGroup();

        animFig_ = (GameObject)EditorGUILayout.ObjectField(animFig_, typeof(GameObject));
        animation_ = (AnimationClip)EditorGUILayout.ObjectField(animation_, typeof(AnimationClip));

        if (animFig_ != null && GUILayout.Button("Extruct Feature")) {
            CallExtractMotionFeature();
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

    void ExtractingMotionFeatures() {
        //Based on these individual frames’ motion 
        //feature values, we can further extract each feature’s mean,
        //median, variance, and also the mean, median, and variance
        //of the feature’s first order forward finite difference.

        // find curve
        //// find node
        //string[] jointName = new string[] {
        //    "Bip01 L UpperArm", "Bip01 R UpperArm", };
        

        // extract distance
        // extract rotation

    }
}

