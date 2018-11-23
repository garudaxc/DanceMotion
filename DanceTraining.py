import tensorflow as tf
import numpy as np
from tensorflow.contrib import rnn
import os.path
import MotionFeature
import matplotlib.pyplot as plt

root = './resource/'
numHidden = 26
batchSize = 64
numSteps = 7
inputDim = 294
numLayers = 1
lableDim = 1
learning_rate = 0.001

ModelFileName = '../../NNModels/DanceModel.ckpt'

def SaveModel(sess, filename, saveMeta = False):
    saver = tf.train.Saver()
    saver.save(sess, filename, write_meta_graph=saveMeta)
    print('model saved')

def FectchMotionCost(totalBeats, cost, indics, start = 0):
    newCost = np.zeros_like(indics, dtype=np.float)

    totalCost = int((totalBeats * (totalBeats-1)) / 2)
    assert totalCost == cost.shape[0]

    for i, k in enumerate(indics, start):
        if i == k:
            newCost[i-start] = 0.0
        else:
            j = i
            if j > k:
                tmp = j
                j = k
                k = tmp

            n = int(totalCost - ((totalBeats-j)*(totalBeats-j-1)) / 2 + k - j - 1)
            newCost[i-start] = cost[n]
    
    return newCost

def SplitSamples(samples, totalBatches, trainBatches):
    samples = samples[:totalBatches * batchSize]
    trainSamples = samples[:trainBatches * batchSize]
    testSamples = samples[trainBatches * batchSize:]
    testBatches = totalBatches - trainBatches
    assert testSamples.shape[0] == testBatches*batchSize
    
    print('train', trainSamples.shape, 'test', testSamples.shape)
    return (trainSamples, testSamples)


def PrepareTrainData():
    files = os.listdir(root)
    files.sort()    

    musicFeatures = []
    motionFeatures = []

    for f in files:
        name = os.path.join(root, f)
        if not os.path.isdir(name):
            continue
        name = os.path.join(root, f, f) + '.mp3'
        if not os.path.exists(name):
            print('error, can not find file ', name)
            continue

        music = MotionFeature.PrepareMusicFeature(name)

        mFeatureName = os.path.join(root, f, 'motion_feature.bin')
        motion = MotionFeature.PrepareMotionFeature(mFeatureName)

        assert music.shape[0] == motion.shape[0]

        print(music.shape, motion.shape)
        # music feature shape 168
        # motion feature shape 126
        # total feature shape 294
        music = music.reshape(-1, 7, music.shape[-1])
        motion = motion.reshape(-1, 7, motion.shape[-1])

        musicFeatures.append(music)
        motionFeatures.append(motion)

    musicFeatures = np.concatenate(musicFeatures)
    motionFeatures = np.concatenate(motionFeatures)
    
    numBeats, motionCost = MotionFeature.LoadMotionSimilarity()
    totalBeats = sum(numBeats)
    assert totalBeats == motionFeatures.shape[0]

    plt.plot(motionCost)
    plt.show()

    return


    totalCost = (totalBeats * (totalBeats - 1)) / 2
    assert totalCost == motionCost.shape[0]

    print(musicFeatures.shape, 'total beats', totalBeats, 'total cost', motionCost.shape[0])

    numBatches = int(totalBeats / batchSize)
    numTrainBatches = int(numBatches * 0.7)
    numTestBatches = numBatches - numTrainBatches

    trainMusic, testMusic = SplitSamples(musicFeatures, numBatches, numTrainBatches)
    trainMotion, testMotion = SplitSamples(motionFeatures, numBatches, numTrainBatches)

    indices = np.arange(0, numTrainBatches * batchSize, dtype=np.int32)
    seqLen = np.array([numSteps] * batchSize)
    
    testIndex = np.arange(numTrainBatches * batchSize, numBatches * batchSize, dtype=np.int32)
    np.random.shuffle(testIndex)
    testMotion = testMotion[testIndex-(numTrainBatches * batchSize)]
    testSample = np.concatenate((testMusic, testMotion), axis = 2)
    testSample = testSample.reshape(-1, batchSize, testSample.shape[1], testSample.shape[2])
    testCost = FectchMotionCost(totalBeats, motionCost, testIndex, numTrainBatches*batchSize)
    testCost = testCost.reshape(-1, batchSize, 1)

    #zeroTestCost = np.zeros((batchSize, 1))

    rnn = BuildRnn()
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    SaveModel(sess, ModelFileName, True)
    
    epch = 400
    currentTrainLoss = np.inf
    notImproveCount = 0
    for j in range(epch):
        loss = []

        np.random.shuffle(indices)
        shuffledMotion = trainMotion[indices]

        samplesX = np.concatenate((trainMusic, shuffledMotion), axis=2)
        samplesX = samplesX.reshape(-1, batchSize, samplesX.shape[1], samplesX.shape[2])
        #print('sample X shape', samplesX.shape)

        shuffledCost = FectchMotionCost(totalBeats, motionCost, indices)
        shuffledCost = shuffledCost.reshape(-1, batchSize, 1)

        assert numTrainBatches == samplesX.shape[0]
        for i in range(numTrainBatches):
            feed_dict={rnn['X']:samplesX[i], rnn['Y']:shuffledCost[i], rnn['seqLen']:seqLen, rnn['learningRate']:learning_rate}
        
            _, l = sess.run([rnn['train_op'], rnn['loss_op']], feed_dict=feed_dict)
            loss.append(l)

        if j % 10 == 0:
            trainLoss = sum(loss) / len(loss)

            testLoss = []
            for k in range(numTestBatches):
                feed_dict={rnn['X']:testSample[k], rnn['Y']:testCost[k], rnn['seqLen']:seqLen}
        
                l = sess.run([rnn['test_loss']], feed_dict=feed_dict)
                testLoss.append(l[0])

            testLoss = sum(testLoss) / len(testLoss)
            print('train loss', trainLoss, 'test loss', testLoss)

            if testLoss < currentTrainLoss:
                currentTrainLoss = testLoss
                notImproveCount = 0
                SaveModel(sess, ModelFileName, False)
            else:
                notImproveCount += 1
                print('not improve count', notImproveCount)
            
            if notImproveCount > 5:
                break


    print('done!')


def BuildRnn():
    bSaveModel = True

    epch = 300
    states = None
    #####################
    
    seqLen = tf.placeholder(tf.int32, [None], name='seqLen')
    X = tf.placeholder(dtype=tf.float32, shape=(batchSize, numSteps, inputDim), name='X')
    Y = tf.placeholder(dtype=tf.float32, shape=(batchSize, lableDim), name='Y')
    #testY = tf.placeholder(dtype=tf.float32, shape=(batchSize, lableDim), name='testY')
    learningRate = tf.placeholder(dtype=tf.float32, name='learn_rate')
    
    weights = tf.Variable(tf.random_normal(shape=[numHidden*2, lableDim]))
    bais = tf.Variable(tf.random_normal(shape=[lableDim]))
    # two states in one layer in forward net, backward net do not need
    #numStateTensor = 2 * numLayers
    #state_tensor = tf.placeholder(dtype=tf.float32, shape=(numStateTensor, batchSize, numHidden), name='input_state')
    #print('state_tensor', state_tensor)
    ###############

    result = {}
    result['seqLen'] = seqLen
    result['X'] = X
    result['Y'] = Y
    result['learningRate'] = learningRate
    
    cells = []
    dropoutCell = []
    for i in range(numLayers * 2):
        c = rnn.LSTMCell(numHidden, use_peepholes=True, forget_bias=1.0)
        cells.append(c)
        c = tf.nn.rnn_cell.DropoutWrapper(c, output_keep_prob=0.6)
        dropoutCell.append(c)
    
    if states == None:
        init_state_fw = None
    else:
        numStates = 2 * numLayers
        # assert states.shape() == 2 * numStates
        states = tf.unstack(states)
        print(len(states), states[0])

        init_state_fw = [None] * numLayers
        for i in range(numLayers):
            init_state_fw[i] = rnn.LSTMStateTuple(states[i * 2 + 0], states[i * 2 + 1])

    output, final_state_fw, final_state_bw = rnn.stack_bidirectional_dynamic_rnn(dropoutCell[0:numLayers], dropoutCell[numLayers:], inputs=X, 
        initial_states_fw=init_state_fw, initial_states_bw=None,
        sequence_length=seqLen, dtype=tf.float32)

    outlayerDim = tf.shape(output)[2]
    output = output[:, -1, :]
    print('output', output)

    prediction = tf.matmul(output, weights) + bais
    print('prediction', prediction)

    loss_op = tf.losses.mean_squared_error(labels=Y, predictions=prediction)
    print(loss_op)

    # Define loss and optimizer
    result['loss_op'] = loss_op

    optimizer = tf.train.AdamOptimizer(learning_rate=learningRate)    
    # optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)

    train_op = optimizer.minimize(loss_op)
    result['train_op'] = train_op
    
    # prediction without dropout
    output, final_state_fw, final_state_bw = rnn.stack_bidirectional_dynamic_rnn(
        cells[0:numLayers], cells[numLayers:], X,        
        initial_states_fw=init_state_fw, initial_states_bw=None,
        sequence_length=seqLen, dtype=tf.float32)
    
    output = output[:, -1, :]
    predictions = tf.add(tf.matmul(output, weights), bais, name='predict_op')
    
    test_loss = tf.losses.mean_squared_error(labels=Y, predictions=predictions)

    result['test_loss'] = test_loss

    return result



def Regress():    
    testMusic = '../../test/siren/siren.mp3'
    filename = os.path.abspath(testMusic)
    music = MotionFeature.PrepareMusicFeature(filename)    
    music = music.reshape(-1, 1, numSteps, music.shape[-1])

    music = music.repeat(batchSize, axis=1)
    print('music feature', music.shape)
    
    # load motion features
    files = os.listdir(root)
    files.sort()    

    motionFeatures = []

    for f in files:
        name = os.path.join(root, f)
        if not os.path.isdir(name):
            continue
        name = os.path.join(root, f, 'motion_feature.bin')
        if not os.path.exists(name):
            print('error, can not find file ', name)
            continue

        motion = MotionFeature.PrepareMotionFeature(name)
        motion = motion.reshape(-1, 7, motion.shape[-1])

        motionFeatures.append(motion)

    motionFeatures = np.concatenate(motionFeatures)
    print('motion feature', motionFeatures.shape)
    
    motionBeats = motionFeatures.shape[0]
    numBatches = int(motionBeats / batchSize)
    print('num batches ', numBatches)
    motionFeatures = motionFeatures[:numBatches * batchSize]
    motionFeatures = motionFeatures.reshape(-1, batchSize, motionFeatures.shape[1], motionFeatures.shape[2])
    print('motion feature', motionFeatures.shape)
    

    
    graphFile = ModelFileName + '.meta'
    saver = tf.train.import_meta_graph(graphFile)

    with tf.Session() as sess:
        
        saver.restore(sess, ModelFileName)
        print('model loaded')

        predict_op = tf.get_default_graph().get_tensor_by_name("predict_op:0")
        print('predict_op', predict_op)         
        X = tf.get_default_graph().get_tensor_by_name('X:0')
        seqLenHolder = tf.get_default_graph().get_tensor_by_name('seqLen:0')
        #output_state = tf.get_default_graph().get_tensor_by_name('output_state:0')
        #input_state = tf.get_default_graph().get_tensor_by_name('input_state:0')
        seqLen = np.array([numSteps] * batchSize)

        epch = music.shape[0]
        for i in range(1):
            print(i)
            feature = music[i]
            feature = feature[np.newaxis, ::]
            feature = feature.repeat(numBatches, axis=0)
            feature = np.concatenate((feature, motionFeatures), axis=3)
            print('feature', feature.shape)

            for j in range(5):
                feed_dict={X:feature[j], seqLenHolder:seqLen}        
                res = sess.run([predict_op], feed_dict=feed_dict)
                print(res)









def Test():
    dir = os.path.dirname(__file__)
    os.chdir(dir)
    print(os.path.abspath('.'))

    PrepareTrainData()
    #Regress()
    #BuildRnn()


    #indices = np.arange(0, 20, dtype=np.int32)
    #np.random.shuffle(indices)

    #print(indices)

    #a = np.array([[1, 2], [5, 2], [7, 4]])
    #print(a)

    #b = a[[1, 0]]
    #print(a)
    #print(b)

    #for i, k in enumerate(a):
    #    print(i, k)
    #    i = 0
    #    print(i, k)

    #numSamples = 5
    #numCost = 10
    #cost = np.arange(0.0, float(numCost), 1.0)
    #indice = np.array([4, 3, 1, 4, 3])
    ##indice = np.array([1, 1, 1, 1, 1])

    #newCost = FectchMotionCost(numSamples, cost, indice)
    #print(cost)
    #print(newCost)




if __name__ == '__main__':
    Test()