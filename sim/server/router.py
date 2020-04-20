import regex
from functools import partial


class Router:
    handlers = None
    def __init__(self, handlers):
        self.handlers = handlers

    def routes_to_capture_groups(self, method):
        token_regex = r"{(\w+)}"
        token_capture_all = r"([^/]+)"
        regexed_routes = []

        for route in method:
            url, handler = route
            capture_groups = regex.findall(token_regex, url)
            regex_route = regex.sub(token_regex, token_capture_all, url)
            regexed_routes.append((regex_route, capture_groups))

        return regexed_routes

    def create_regex(self, regexed_routes):
        return  r"^(?|" + r"|".join("(?P<route%i>%s)" % (i, route) for i, (route, captures) in enumerate(regexed_routes)) + r")$"

    def match(self, method, path):
        try:
            routes = self.handlers.get(method)
            routes_and_capture = self.routes_to_capture_groups(routes)
            rules =  self.create_regex(routes_and_capture)

            matches = regex.match(rules, path)
            # Take one and only capture group
            capture = matches.captures()[0]
            # Get all groups
            groups = matches.groups()

            if capture:
                for i, g in enumerate(groups):
                    if (g == capture):
                        route, handler = routes[i]
                        keyed_variables = {}
                        j = i+1 # Move on to capture groups
                        for variable in routes_and_capture[i][1]:
                            keyed_variables[variable] = groups[j]
                            j += 1
                        
                        return partial(handler, **keyed_variables)
            else:
                raise Exception("Route Not found")
        except Exception as e:
            return
