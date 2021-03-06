import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile

model_dir = '/home/jehyunpark/Downloads/crnn/results/'
image_path = '/home/jehyunpark/Downloads/crnn/images/handclapping/'


BOTTLENECK_TENSOR_NAME = 'pool_3/_reshape:0'
JPEG_DATA_TENSOR_NAME = 'DecodeJpeg/contents:0'
RESIZED_INPUT_TENSOR_NAME = 'ResizeBilinear:0'


filenames = sorted(os.listdir(image_path), key = lambda a:a[6:11])[200:210]

def create_inception_graph():
  """"Creates a graph from saved GraphDef file and returns a Graph object.
  Returns:
    Graph holding the trained Inception network, and various tensors we'll be
    manipulating.
  """
  with tf.Graph().as_default() as graph:
    model_filename = os.path.join(
        model_dir, 'output_graph.pb')
    with gfile.FastGFile(model_filename, 'rb') as f:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(f.read())
      bottleneck_tensor, jpeg_data_tensor, resized_input_tensor = (
          tf.import_graph_def(graph_def, name='', return_elements=[
              BOTTLENECK_TENSOR_NAME, JPEG_DATA_TENSOR_NAME,
              RESIZED_INPUT_TENSOR_NAME]))
  return graph, bottleneck_tensor, jpeg_data_tensor, resized_input_tensor

def run_bottleneck_on_image(sess, image_data, image_data_tensor,
                            bottleneck_tensor):
  """Runs inference on an image to extract the 'bottleneck' summary layer.
  Args:
    sess: Current active TensorFlow Session.
    image_data: String of raw JPEG data.
    image_data_tensor: Input data layer in the graph.
    bottleneck_tensor: Layer before the final softmax.
  Returns:
    Numpy array of bottleneck values.
  """
  bottleneck_values = sess.run(
      bottleneck_tensor,
      {image_data_tensor: image_data})
  bottleneck_values = np.squeeze(bottleneck_values)
  return bottleneck_values

def get_frames():
    i = 0
    graph, bottleneck_tensor, jpeg_data_tensor, resized_image_tensor = (
            create_inception_graph())

    with tf.Session(graph=graph) as sess:
        # init = tf.global_variables_initializer()
        # sess.run(init)
        for filename in filenames:
            full_filename = os.path.join(image_path,filename)
            if i == 0:
                jpeg_data = gfile.FastGFile(full_filename, 'rb').read()
                frames = run_bottleneck_on_image(sess, jpeg_data, jpeg_data_tensor, bottleneck_tensor)[np.newaxis,:]
                i +=1
            elif len(frames) < 10:
                jpeg_data = gfile.FastGFile(full_filename, 'rb').read()
                frames = np.concatenate((frames, run_bottleneck_on_image(sess, jpeg_data, jpeg_data_tensor, bottleneck_tensor)[np.newaxis,:]), axis = 0)
    return frames[np.newaxis,:,:]


 
    
    
