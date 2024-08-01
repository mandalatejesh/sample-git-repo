import math

def direction(prev_point, next_point):
     # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
    # Convert to degree
    track_direction = math.degrees(track_direction)
    return track_direction

def angle_with_x(prev_point, next_point):
    angle = direction(prev_point, next_point)
    if angle > 0 and next_point[1] < prev_point[1]:
        return (angle + 180)
    if angle < 0:
        angle += 360
        if next_point[1] > prev_point[1]:
            angle -= 180
        return angle
    return angle

def transform_theta(point, angle):
    x = point[0]
    y = point[1]
    radian = math.radians(angle)
    return [x*math.cos(radian) + y*math.sin(radian), y*math.cos(radian) - x*math.sin(radian)]

def reward_function(params):
    '''
    Example of penalize steering, which helps mitigate zig-zag behaviors
    '''

    '''
    {
    "all_wheels_on_track": Boolean,        # flag to indicate if the agent is on the track
    "x": float,                            # agent's x-coordinate in meters
    "y": float,                            # agent's y-coordinate in meters
    "closest_waypoints": [int, int],       # indices of the two nearest waypoints.
    "distance_from_center": float,         # distance in meters from the track center 
    "is_crashed": Boolean,                 # Boolean flag to indicate whether the agent has crashed.
    "is_left_of_center": Boolean,          # Flag to indicate if the agent is on the left side to the track center or not. 
    "is_offtrack": Boolean,                # Boolean flag to indicate whether the agent has gone off track.
    "is_reversed": Boolean,                # flag to indicate if the agent is driving clockwise (True) or counter clockwise (False).
    "heading": float,                      # agent's yaw in degrees
    "progress": float,                     # percentage of track completed
    "speed": float,                        # agent's speed in meters per second (m/s)
    "steering_angle": float,               # agent's steering angle in degrees
    "steps": int,                          # number steps completed
    "track_length": float,                 # track length in meters.
    "track_width": float,                  # width of the track
    "waypoints": [(float, float), ]        # list of (x,y) as milestones along the track center
}

Bad:
    is_crashed
    if_offtrack
    is_reversed
Good:



    
    '''
    
    # Read input parameters
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    steering = abs(params['steering_angle']) # Only need the absolute steering angle

    # Calculate 3 marks that are farther and father away from the center line
    marker_1 = 0.15 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    speed = params['speed']    
    max_speed = 3
    # Give higher reward if the car is closer to center line and vice versa
    if distance_from_center <= marker_1:
        reward = 1
    elif distance_from_center <= marker_2:
        reward = 0.5
    elif distance_from_center <= marker_3:
        reward = 0.1
    else:
        reward = 1e-3  # likely crashed/ close to off track
    
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']

    # Calculate the direction of the center line based on the closest waypoints
    next_next_point = waypoints[(closest_waypoints[1]+1)%len(waypoints)]
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = direction(prev_point, next_point)
    tr_next_point = transform_theta(next_point, track_direction)
    tr_next_next_point = transform_theta(next_next_point, track_direction)
    angle = angle_with_x(tr_next_point, tr_next_next_point)
    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff
        
    desired_speed = (240-7*direction_diff)/60
    should_be_left = True
    if angle < 180:
        should_be_left = False

    # Penalize the reward if the difference is too large
    DIRECTION_THRESHOLD = 15.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward += 1e-3
        if speed < 0.7:
            reward += 0.2
    elif (abs(speed - desired_speed) < 0.3):
        reward += 0.3
        
    if not (should_be_left ^ params['is_left_of_center']):
        reward += 0.3
        
    

    

    # Steering penality threshold, change the number based on your action space setting
    # ABS_STEERING_THRESHOLD = 20

    # # Penalize reward if the car is steering too much
    # if steering > ABS_STEERING_THRESHOLD:
    #     reward += 1e-3
    # else:
    #     reward += 0.2

    return float(reward)