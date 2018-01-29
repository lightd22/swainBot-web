import tensorflow as tf

class Model:
    def __init__(self, path_to_model):
        self._path_to_model = path_to_model
        tf.reset_default_graph()
        self.sess = tf.Session()

        self.sess.run(tf.global_variables_initializer())
        saver = tf.train.import_meta_graph("{path}.ckpt.meta".format(path=path_to_model))
        saver.restore(self.sess,"{path}.ckpt".format(path=path_to_model))
        self._predict_q_values = tf.get_default_graph().get_tensor_by_name("online/valid_q_vals:0")
        self._predict_action = tf.get_default_graph().get_tensor_by_name("online/prediction:0")
        self._primary_input = tf.get_default_graph().get_tensor_by_name("online/inputs:0")
        self._valid_actions = tf.get_default_graph().get_tensor_by_name("online/valid_actions:0")
        #self._train = tf.get_default_graph().get_tensor_by_name("online/update")
        print("Model closed..")

    def __del__(self):
        self.sess.close()
        print("Model closed..")

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
