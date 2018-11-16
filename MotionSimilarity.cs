using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;


public interface IUpdateProgress
{
    void Update(string info, float progress);
}


public class MotionSimilarity
{
    public static readonly int NumSamplesPerBeat = 7;
    List<FrameData> frames_;
    List<float> cost_esti_;
    int totalBeats_ = 0;
    Quaternion[,,] quat_;


    public class FrameData
    {
        public string name;
        public int numBeats;
        public float startTime;
        public float beatTime;
    }

    public class MotionFrame
    {
        public float minCost;
        public int index0;
        public int index1;
    }

    public MotionSimilarity() {
    }

    public FrameData GetFrameData(int index) {
        return frames_[index];
    }

    public List<float> GetCostEstimate() {
        return cost_esti_;
    }
    
    public void IndexToMotionClip(int index, ref int motionIndex, ref int beat) {

        int m = 0;
        int current = index;
        while(current > frames_[m].numBeats) {
            current -= frames_[m].numBeats;
            m++;
        }

        motionIndex = m;
        beat = current;
    }

    class DummyUpdater : IUpdateProgress
    {
        public void Update(string info, float progress) {
        }
    };
    public static void TestMotionFrameByIndex() {

        MotionSimilarity ms = new MotionSimilarity();
        ms.CalcMotionSimilarity(new DummyUpdater());

        var cost = ms.GetCostEstimate();

        for (int i = 0; i < 10; i++) {
            int ii = MotionSimilarity.FindSmallestAfter(cost, i, float.NegativeInfinity, float.PositiveInfinity);
            var frame = ms.MotionFrameByIndex(ii);
            float c = MotionSimilarity.MotionSeqCost(ms.quat_, frame.index0, frame.index1);
            Debug.LogFormat("cost 0 {0} cost 1 {1}", cost[ii], c);
        }

        var largest = MotionSimilarity.FindLargestAfter(cost, 0, float.NegativeInfinity, float.PositiveInfinity);
        Debug.LogFormat("largest value {0}", cost[largest]);
    }


    public MotionFrame MotionFrameByIndex(int globalIndex) {
        if (cost_esti_.Count != EstimateCostCount() || globalIndex >= cost_esti_.Count) {
            throw new Exception("value count invalid");
        }

        int index = globalIndex;
        int a = totalBeats_ - 1;
        while (index >= a) {
            index -= a;
            a--;
        }

        int i0 = totalBeats_ - 1 - a;
        int i1 = i0 + 1 + index;

        var frame = new MotionFrame() {
            minCost = cost_esti_[globalIndex],
            index0 = i0,
            index1 = i1
        };

        return frame;
    }

    public List<FrameData> IndexMotionSeg() {
        var path = "Assets/DanceMotion/resource/";
        var dirs = Directory.GetDirectories(path);
        Array.Sort(dirs);

        List<FrameData> frameData = new List<FrameData>();

        int count = 0;
        totalBeats_ = 0;
        foreach (var d in dirs) {
            var songName = d.Substring(path.Length);

            var musicInfo = Utility.LoadMusicInfo(d);

            float bpm = musicInfo["bpm"];
            float enterTime = musicInfo["et"];
            float motionStart = musicInfo["start"];
            float motionEnd = musicInfo["end"];

            // 一拍中分6个window，window间50%重叠，每个window采样6次
            // 一拍共6 * 3.5=21个采样点
            float beat = 60.0f / bpm;

            float start = Math.Max(enterTime, motionStart);
            start = start - (start - enterTime) % beat + beat;
            float end = motionEnd - (motionEnd - enterTime) % beat;
            int numBeats = Mathf.RoundToInt((end - start) / beat);

            var frame = new FrameData() {
                name = songName,
                numBeats = numBeats,
                beatTime = beat,
                startTime = start,
            };
            frameData.Add(frame);

            totalBeats_ += numBeats;
            count++;
        }

        return frameData;
    }

    public int EstimateCostCount() {
        int count = 0;
        checked {
            count = (totalBeats_ * (totalBeats_ - 1)) / 2;
        }

        Debug.LogFormat("count {0} size {1}MB log {2}", count, 4 * count / (1024 * 1024), Mathf.Log(count, 2));
        return count;
    }

    public void CalcMotionSimilarity(IUpdateProgress updater) {
        frames_ = IndexMotionSeg();

        updater.Update("collect frames info", 0.0f);
        string[] jointName = new string[] {
                "Bip01 L Thigh",
                "Bip01 R Thigh",
                "Bip01 L Calf",
                "Bip01 R Calf",
                "Bip01 L UpperArm",
                "Bip01 R UpperArm",
                "Bip01 L Forearm",
                "Bip01 R Forearm",
            };


        quat_ = new Quaternion[totalBeats_, NumSamplesPerBeat, jointName.Length];

        int beatIndex = 0;

        foreach (var frame in frames_) {
            var resName = string.Format("Assets/DanceMotion/resource/{0}/{0}.prefab", frame.name);

            Debug.Log("load " + resName);

            var res = (GameObject)AssetDatabase.LoadAssetAtPath(resName, typeof(GameObject));
            Debug.Log("load " + resName);
            var inst = GameObject.Instantiate(res);

            Transform[] joints = new Transform[jointName.Length];
            for (int i = 0; i < jointName.Length; i++) {
                GameObject o = Utility.FindGameObjectByName_r(inst, jointName[i]);
                if (o == null) {
                    Debug.LogFormat("can not found gameobject {0}", jointName[i]);
                } else {
                    joints[i] = o.transform;
                }
            }

            Animation animation = inst.GetComponent<Animation>();
            AnimationState state = animation["Take 001"];
            state.weight = 1.0f;
            state.enabled = true;

            float dt = frame.beatTime / (float)NumSamplesPerBeat;
            float invdt = 1.0f / dt;
            
            for (int i = 0; i < frame.numBeats; i++) {
                for (int j = 0; j < NumSamplesPerBeat; j++) {
                    float time = frame.startTime + dt * (i * NumSamplesPerBeat + j);
                    state.time = time;
                    animation.Sample();

                    for (int k = 0; k < joints.Length; k++) {
                        quat_[beatIndex, j, k] = joints[k].localRotation;
                    }
                }
                beatIndex++;
            }
            
            GameObject.DestroyImmediate(inst);
        }

        int numCost = EstimateCostCount();
        cost_esti_ = new List<float>();
        for (int i = 0; i < totalBeats_; i++) {
            for (int j = i + 1; j < totalBeats_; j++) {
                float cost = MotionSeqCost(quat_, i, j);
                cost_esti_.Add(cost);
            }

            float progress = cost_esti_.Count / (float)numCost;
            updater.Update("calculate cost", progress);
        }

        if (cost_esti_.Count != numCost) {
            Debug.LogFormat("cost {0} estimate {1}", cost_esti_.Count, numCost);
            throw new Exception("value count invalid");
        }

        updater.Update("save to file", 1.0f);

        FileStream fs = new FileStream("MotionCost.bin", FileMode.Create, FileAccess.Write);
        BinaryWriter bw = new BinaryWriter(fs);
        bw.Write(frames_.Count);
        foreach (var f in frames_) {
            var chars = f.name.ToCharArray();
            bw.Write(chars.Length);
            bw.Write(chars);
            bw.Write(f.numBeats);
            Debug.LogFormat("chars {0} {1} {2}", chars.Length, f.name, f.numBeats);
        }

        bw.Write(cost_esti_.Count);
        foreach (var v in cost_esti_) {
            bw.Write(v);
        }
        bw.Close();
        fs.Close();

        Debug.Log("Done!");
    }

    static int IndexOfMaximum<T>(IList<T> l) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = 0;
        T maxinum = l[index];
        for (int i = 1; i < l.Count; i++) {
            if (l[i].CompareTo(maxinum) > 0) {
                index = i;
                maxinum = l[i];
            }
        }
        return index;
    }

    static int IndexOfMinimum<T>(IList<T> l) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = 0;
        T minimum = l[index];
        for (int i = 1; i < l.Count; i++) {
            if (l[i].CompareTo(minimum) < 0) {
                index = i;
                minimum = l[i];
            }
        }
        return index;
    }


    public static int FindLargestAfter<T>(IList<T> l, int serialNum, T NegativeInfinity, T infinity) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = -1;
        T serialMax = infinity;
        for (int i = 0; i < serialNum + 1; i++) {
            int currIndex = -1;
            T cmax = NegativeInfinity;
            for (int j = 0; j < l.Count; j++) {
                if (l[j].CompareTo(cmax) > 0 && l[j].CompareTo(serialMax) < 0) {
                    currIndex = j;
                    cmax = l[j];
                }
            }

            serialMax = cmax;
            index = currIndex;
        }

        return index;
    }


    public static int FindSmallestAfter<T>(IList<T> l, int serialNum, T NegativeInfinity, T infinity) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = -1;
        T serialMin = NegativeInfinity;
        for (int i = 0; i < serialNum + 1; i++) {
            int currIndex = -1;
            T cmin = infinity;
            for (int j = 0; j < l.Count; j++) {
                if (l[j].CompareTo(cmin) < 0 && l[j].CompareTo(serialMin) > 0) {
                    currIndex = j;
                    cmin = l[j];
                }
            }

            serialMin = cmin;
            index = currIndex;
        }

        return index;
    }

    static float MotionSeqCost(Quaternion[,,] quat, int index0, int index1) {
        var weights = new float[] {
                1.0000f,
                1.0000f,
                0.0901f,
                0.0901f,
                0.7884f,
                0.7884f,
                0.0247f,
                0.0247f,
            };

        float cost = 0.0f;
        for (int i = 0; i < NumSamplesPerBeat; i++) {
            for (int j = 0; j < weights.Length; j++) {
                float omiga = Quaternion.Angle(
                    quat[index0, i, j],
                    quat[index1, i, j]);

                cost += Math.Abs(omiga) * weights[j];
            }
        }

        return cost;
    }

}
