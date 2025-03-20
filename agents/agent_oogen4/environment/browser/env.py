import gymnasium as gym

class BrowserEnv(gym.Env):
    """
    Gymnasium environment for controlling a Browser via a Browser Control Server.
    """

    def __init__(self):
        pass

    def step(self, action):
        """
        Executes an action and returns observation, reward, done, info.
        """

        observation = ""
        reward = 0
        terminated = False # done
        truncated = False
        info = {} # Contains auxiliary diagnostic information (helpful for debugging, learning, and logging).
        
        return observation, reward, terminated , truncated, info

    def reset(self):
        """
        Resets the environment (reloads VM snapshot).
        """
        
        observation = ""
        info = {}

        return observation, info

    def render(self, mode="human"):
        """
        Renders the current environment state (optional).
        """
        pass

    def close(self):
        """
        Clean up resources.
        """
        pass
