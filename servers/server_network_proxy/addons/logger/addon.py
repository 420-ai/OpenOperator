class LoggerAddon:
    def request(self, flow):
        print("LOGGER ADDON SAW:", flow.request.pretty_url)
