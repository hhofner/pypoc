class NetworkData:
    def __init__(self):
        '''
    Initialize data dictionary that is never to be accessed directly. Naming convention is
    to append either "_list" or "_value" to data key.
    '''
    self.title = ''
    self.author = ''
    self.data = {}

    # List of total network throughput value, per time.
    self.data['throughput_list'] = []

    # List of generated packets by any node, per time.
    self.data['generated_packet_list'] = []

    # Current total network throughput value.
    self.data['throughput_value'] = 0

    # Current step value for one `tick`
    self.data['step_value'] = 0

    # Current value of total generated packets.
    self.data['generated_packet_count_value'] = 0

    # Current value of total bytes sent
    self.data['total_byte_count_value'] = 0

    # Value of start time of data run
    self.data['start_time_value'] = 0

    # Value of end time of data run
    self.data['end_time_value'] = 0

    # Value of current packet drop rate
    self.data['packet_drop_rate_value'] = 0

def data_save_to_file(self, network, filename=None, data_filepath=None, config_file=None):
    '''
    Save all metadata to file, as well as all nodes data.
    :param network: PyPocNetwork object
    :return None:
    '''
    if filename is None:
        filename = f'{self.title}_{self.data["start_time_value"].strftime("%d%b%y_%H_%M_%S")}.csv'

    if data_filepath is None:
        data_filepath = f'./simulation_data/' + filename

    with open(data_filepath, mode='w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['title', self.title])
        writer.writerow(['author', self.author])
        for key in self.data.keys():
            if isinstance(self.data[key], list):
                writer.writerow([key] + self.data[key])
            else:
                writer.writerow([key] + [self.data[key]])


