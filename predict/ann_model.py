import tensorflow as tf
import numpy as np

class Model:
    def __init__(self, path_to_model):
        self._path_to_model = path_to_model
        #tf.reset_default_graph()
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)

        #self.sess.run(tf.global_variables_initializer())
        with self.graph.as_default():
            saver = tf.train.import_meta_graph("{path}.ckpt.meta".format(path=path_to_model))
            saver.restore(self.sess,"{path}.ckpt".format(path=path_to_model))
        print("Model opened..")

    def __del__(self):
        try:
            self.sess.close()
            del self.sess
        finally:
            print("Model closed..")

    def predict(self):
        raise NotImplementedError

    def predict_action(self):
        raise NotImplementedError

class QModel(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._predict_q_values = self.graph.get_tensor_by_name("online/valid_q_vals:0")
        self._predict_action = self.graph.get_tensor_by_name("online/prediction:0")
        self._primary_input = self.graph.get_tensor_by_name("online/inputs:0")
        self._valid_actions = self.graph.get_tensor_by_name("online/valid_actions:0")
        #self._train = tf.get_default_graph().get_tensor_by_name("online/update")

    def predict(self, states):
        """
        Feeds state into model and returns current predicted Q-values.
        Args:
            states (list of DraftStates): states to predict from
        Returns:
            predicted_Q (numpy array): model estimates of Q-values for actions from input states.
              predicted_Q[k,:] holds Q-values for state states[k]
        """
        primary_inputs = [state.format_state() for state in states]
        valid_actions = [state.get_valid_actions() for state in states]

        predicted_Q = self.sess.run(self._predict_q_values,
                                feed_dict={self._primary_input:primary_inputs,
                                self._valid_actions:valid_actions})
        return predicted_Q

    def predict_action(self, states):
        """
        Feeds state into model and return recommended action to take from input state based on estimated Q-values.
        Args:
            state (list of DraftStates): states to predict from
        Returns:
            predicted_action (numpy array): array of integer representations of actions recommended by model.
        """
        primary_inputs = [state.format_state() for state in states]
        valid_actions = [state.get_valid_actions() for state in states]

        predicted_actions = self.sess.run(self._predict_action,
                                feed_dict={self._primary_input:primary_inputs,
                                self._valid_actions:valid_actions})
        return predicted_actions

class SoftmaxModel(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._predict = self.graph.get_tensor_by_name("softmax_model/action_probabilites:0")
        self._input = self.graph.get_tensor_by_name("softmax_model/inputs:0")
        self._valid_actions = self.graph.get_tensor_by_name("softmax_model/valid_actions:0")
        self._predicted_action = self.graph.get_tensor_by_name("softmax_model/predictions:0")

    def predict(self, states):
        """
        Feeds state into model and returns current predicted probabilities
        Args:
            states (list of DraftStates): states to predict from
        Returns:
            probabilities (numpy array): model estimates of probabilities for actions from input states.
              probs[k,:] holds probs for state states[k]
        """
        inputs = [state.format_state() for state in states]
        valid_actions = [state.get_valid_actions() for state in states]

        feed_dict = {self._input:np.stack(inputs,axis=0),
                     self._valid_actions:np.stack(valid_actions,axis=0)}
        print(self.sess.graph is self.graph)
        probs = self.sess.run(self._predict,
                                feed_dict=feed_dict)
        return probs

    def predict_action(self, states):
        """
        Feeds state into model and return recommended action to take from input state based on estimated probabilities.
        Args:
            state (list of DraftStates): states to predict from
        Returns:
            predicted_action (numpy array): array of integer representations of actions recommended by model.
        """
        inputs = [state.format_state() for state in states]
        valid_actions = [state.get_valid_actions() for state in states]

        feed_dict = {self._input:np.stack(inputs,axis=0),
                     self._valid_actions:np.stack(valid_actions,axis=0)}
        actions = self.sess.run(self._predicted_action,
                                feed_dict=feed_dict)
        return actions
