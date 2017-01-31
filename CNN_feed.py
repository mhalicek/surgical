
# coding: utf-8

# Trains and Evaluates the Surgical HS Imaging network using a feed dictionary
# ========================================

# In[1]:

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf
import os
import SurgicalCNN 
import patch_size
# import IndianPines_data_set as input_data
import Spatial_dataset as input_data

aaa = time.time()
# Declare model parameters as external flags
# -------------------------------------

# In[2]:
flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 0.01, 'Initial learning rate.')
flags.DEFINE_integer('max_steps', 250000, 'Number of steps to run trainer.')
flags.DEFINE_integer('conv1', 500, 'Number of filters in convolutional layer 1.')
flags.DEFINE_integer('conv2', 100, 'Number of filters in convolutional layer 2.')
flags.DEFINE_integer('hidden1', 91, 'Number of units in hidden layer 1.')
flags.DEFINE_integer('hidden2', 84, 'Number of units in hidden layer 2.')
flags.DEFINE_integer('batch_size', 100, 'Batch size.  '
                     'Must divide evenly into the dataset sizes.')
# flags.DEFINE_string('train_dir', '1.mat', 'Directory to put the training data.')


# In[3]:

learning_rate = 0.01 #0.01
num_epochs = 20
max_steps = 250000 #4000
IMAGE_SIZE = patch_size.patch_size
conv1 = 500 #500
conv2 = 100 #100
fc1 = 91, #200
fc2 = 84 #84
batch_size = 100
TRAIN_FILES = 53 ####CHANGE FOR TRAINING SET
TEST_FILES = 41 ####CHANGE FOR TESTING SET
DATA_PATH = os.path.join(os.getcwd(),"Data/Train/All")


# In[4]:

def placeholder_inputs(batch_size):
    """Generate placeholder variables to represent the input tensors.
    These placeholders are used as inputs by the rest of the model building
    code and will be fed from the downloaded data in the .run() loop, below.
    Args:
    batch_size: The batch size will be baked into both placeholders.
    Returns:
    images_placeholder: Images placeholder.
    labels_placeholder: Labels placeholder.
    """
    # Note that the shapes of the placeholders match the shapes of the full
    # image and label tensors, except the first dimension is now batch_size
    # rather than the full size of the train or test data sets.
    images_placeholder = tf.placeholder(tf.float32, shape=(batch_size, SurgicalCNN
                                                           .IMAGE_PIXELS))
    labels_placeholder = tf.placeholder(tf.int32, shape=(batch_size))
    return images_placeholder, labels_placeholder


# In[5]:

def fill_feed_dict(data_set, images_pl, labels_pl):
    """Fills the feed_dict for training the given step.
    A feed_dict takes the form of:
    feed_dict = {
      <placeholder>: <tensor of values to be passed for placeholder>,
      ....
    }
    Args:
    data_set: The set of images and labels, from input_data.read_data_sets()
    images_pl: The images placeholder, from placeholder_inputs().
    labels_pl: The labels placeholder, from placeholder_inputs().
    Returns:
    feed_dict: The feed dictionary mapping from placeholders to values.
    """
    # Create the feed_dict for the placeholders filled with the next
    # `batch size ` examples.
    images_feed, labels_feed = data_set.next_batch(batch_size)
    feed_dict = {
      images_pl: images_feed,
      labels_pl: labels_feed,
    }
    return feed_dict


# In[6]:

def do_eval(sess,
            eval_correct,
            images_placeholder,
            labels_placeholder,
            data_set):
    """Runs one evaluation against the full epoch of data.
    Args:
    sess: The session in which the model has been trained.
    eval_correct: The Tensor that returns the number of correct predictions.
    images_placeholder: The images placeholder.
    labels_placeholder: The labels placeholder.
    data_set: The set of images and labels to evaluate, from
      input_data.read_data_sets().
    """
    # And run one epoch of eval.
    true_count = 0  # Counts the number of correct predictions.
    steps_per_epoch = data_set.num_examples // batch_size
    num_examples = steps_per_epoch * batch_size
    for step in xrange(steps_per_epoch):
        feed_dict = fill_feed_dict(data_set,
                                   images_placeholder,
                                   labels_placeholder)
        true_count += sess.run(eval_correct, feed_dict=feed_dict)
    precision = true_count / num_examples
    print('  Num examples: %d  Num correct: %d  Precision @ 1: %0.04f' %
        (num_examples, true_count, precision))
    f = open('Error_rate.txt','a')
    f.write('%f\n'%(precision))
    f.close()


# In[7]:

def add_DataSet(first,second):
    temp_image = np.concatenate((first.images,second.images),axis=0)
    temp_labels = np.concatenate((first.labels,second.labels),axis=0)
    temp_image = temp_image.reshape(temp_image.shape[0],IMAGE_SIZE,IMAGE_SIZE,91)
    temp_image = np.transpose(temp_image,(0,3,1,2))
    temp_labels = np.transpose(temp_labels)
    return input_data.DataSet(temp_image,temp_labels)


# In[8]:

def run_training():
    """Train MNIST for a number of steps."""
    # Get the sets of images and labels for training, validation, and
    # test on IndianPines.
    
    """Concatenating all the training and test mat files"""
    i=0
    for filename in os.listdir(DATA_PATH):
        if filename.startswith('Train_'):
	    print(os.path.join(DATA_PATH, filename))
            data_sets = input_data.read_data_sets(os.path.join(DATA_PATH, filename), 'train')
            if(i==0):
            	Training_data = data_sets
		i=1
            	continue
            else:
            	Training_data = add_DataSet(Training_data,data_sets)

    i=0
    for filename in os.listdir(DATA_PATH):
	if filename.startswith('Val_'):
	    print(os.path.join(DATA_PATH, filename))
            data_sets = input_data.read_data_sets(os.path.join(DATA_PATH, filename), 'train')
            if(i==0):
            	Validation_data = data_sets
		i=1
            	continue
            else:
            	Validation_data = add_DataSet(Validation_data,data_sets)
    
    i=0 
    for filename in os.listdir(DATA_PATH):
	if filename.startswith('Test_'):
	    print(os.path.join(DATA_PATH, filename))
            data_sets = input_data.read_data_sets(os.path.join(DATA_PATH, filename),'test')
            if(i==0):
            	Test_data = data_sets
		i=1
            	continue
            else:
            	Test_data = add_DataSet(Test_data,data_sets)

    #for i in range(TEST_FILES):
        #data_sets = input_data.read_data_sets(os.path.join(DATA_PATH, 'Test_'+str(IMAGE_SIZE)+'_'+str(i+1)+'.mat'),'test')
        #if(i==0):
            #Test_data = data_sets
            #continue
        #else:
            #Test_data = add_DataSet(Test_data,data_sets)
        
    # Tell TensorFlow that the model will be built into the default Graph.
    with tf.Graph().as_default():
    # Generate placeholders for the images and labels.
        images_placeholder, labels_placeholder = placeholder_inputs(FLAGS.batch_size)

        # Build a Graph that computes predictions from the inference model.
        logits = SurgicalCNN.inference(images_placeholder,
                                 FLAGS.conv1,
                                 FLAGS.conv2,        
                                 FLAGS.hidden1,
                                 FLAGS.hidden2)

        # Add to the Graph the Ops for loss calculation.
        loss = SurgicalCNN.loss(logits, labels_placeholder)

        # Add to the Graph the Ops that calculate and apply gradients.
        train_op = SurgicalCNN.training(loss, FLAGS.learning_rate)

        # Add the Op to compare the logits to the labels during evaluation.
        eval_correct = SurgicalCNN.evaluation(logits, labels_placeholder)

        # Build the summary operation based on the TF collection of Summaries.
    #    summary_op = tf.merge_all_summaries()

        # Add the variable initializer Op.
        init = tf.initialize_all_variables()# -> Deprecated March 2017
	#init = tf.global_variables_initializer()

        # Create a saver for writing training checkpoints.
        saver = tf.train.Saver()

        # Create a session for running Ops on the Graph.
        sess = tf.Session()

        # Instantiate a SummaryWriter to output summaries and the Graph.
    #    summary_writer = tf.train.SummaryWriter(FLAGS.train_dir, sess.graph)

        # And then after everything is built:

        # Run the Op to initialize the variables.
        sess.run(init)

        # Start the training loop.
        for step in xrange(FLAGS.max_steps):
            start_time = time.time()

            # Fill a feed dictionary with the actual set of images and labels
            # for this particular training step.
            feed_dict = fill_feed_dict(Training_data,
                                     images_placeholder,
                                     labels_placeholder)

            # Run one step of the model.  The return values are the activations
            # from the `train_op` (which is discarded) and the `loss` Op.  To
            # inspect the values of your Ops or variables, you may include them
            # in the list passed to sess.run() and the value tensors will be
            # returned in the tuple from the call.
            _, loss_value = sess.run([train_op, loss],
                                   feed_dict=feed_dict)

            duration = time.time() - start_time

            # Write the summaries and print an overview fairly often.
            if step % 50 == 0:
            # Print status to stdout.
                print('Step %d: loss = %.2f (%.3f sec)' % (step, loss_value, duration))
            # Update the events file.
    #             summary_str = sess.run(summary_op, feed_dict=feed_dict)
    #             summary_writer.add_summary(summary_str, step)
    #             summary_writer.flush()

            # Save a checkpoint and evaluate the model periodically.
            if (step + 1) % 50000 == 0 or (step + 1) == FLAGS.max_steps or (step+1) == 1000:
                saver.save(sess, 'model-spatial-CNN-'+str(IMAGE_SIZE)+'X'+str(IMAGE_SIZE)+'.ckpt', global_step=step)

            # Evaluate against the training set.
                print('Training Data Eval:')
                do_eval(sess,
                        eval_correct,
                        images_placeholder,
                        labels_placeholder,
                        Training_data)
                print('Test Data Eval:')
                do_eval(sess,
                        eval_correct,
                        images_placeholder,
                        labels_placeholder,
                        Test_data)
            # Evaluate against the validation set.
                print('Validation Data Eval:')
                do_eval(sess,
                        eval_correct,
                        images_placeholder,
                        labels_placeholder,
                        Validation_data)
                # Evaluate against the test set.
    #             print('Test Data Eval:')
    #             do_eval(sess,
    #                     eval_correct,
    #                     images_placeholder,
    #                     labels_placeholder,
    #                     data_sets.test)


# In[9]:

run_training()

print('Ran for %f m' %((time.time()-aaa)/60))
# In[ ]:



