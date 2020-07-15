class TensorQNetwork:
    def __init__(self, hidden_layers_count, gamma, learning_rate, input_size=16, output_size=4):
        '''
        '''
        # This is the output of the network
        self.q_target = tf.placeholder(shape=(None, ouput_size), dtype=tf.float32)

        # Reward
        self.r = tf.placeholder(shape=None, dtype=tf.float32)

        self.states = tf.placeholder(shape=(None, input_size), dtype=tf.float32)

        self.enum_actions = tf.placeholder(shape=(None, 2), dtype=tf.int32)

        # Placeholder variable, layers will be the same size as the state
        layer_shape = self.states

        for layer in hidden_layers_count:
            layer = tf.layers.dense(inputs=layer, units=1, activation=tf.nn.relu,
                    kernel_initializer=tf.contrib.layers.xavier_initializer(seed=seed))

        self.output = tf.layers.dense(inputs=layer, units=output_size,
                kernel_initializer=tf.contrib.layers.xavier_initializer(seed))

        self.predictions = tf.gather_nd(self.output, indices=self.enum_actions)
        self.labels = self.r + gamma * tf.reduce_max(self.q_target, axis=1)
        self.cost = tf.reduce_mean(tf.losees.mean_squared_error(labels=self.labels, predictions=self.predictions))
        self.optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(self.cost)

class PytorchQNetwork:
    def __init__(self):
        super().__init__()
        # Define NN here
        self.fc1 = nn.Linear(16, 12)
        self.fc2 = nn.Linear(12, 8)
        self.fc3 = nn.Linear(8, 4)

    # This could be called with either one element, or with a batch (for optimization)
    # so, it will return a tensor [[q-values], [q-values2],...]
    def forward(self, x):
        # Define flow here
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return x
