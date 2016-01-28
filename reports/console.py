

from __future__ import print_function


class ConsoleReporter(object):

    def write(self, instances, volumes):

        instances.sort(key=lambda x: x.cost, reverse=True)
        total_cost = 0
        total_cost_per_hour = 0
        for instance in instances:

            total_cost += instance.cost
            total_cost_per_hour += instance.cost_per_hour
            print("Instances")
            print("{} ${:.2f} \t{} \t{} \t{} \t{} \t{}".format(
                                            instance.launchedAtUtc,
                                            instance.cost,
                                            instance.identifier,
                                            instance.aws_instance_type,
                                            instance.aws_region,
                                            instance.keyname,
                                            instance.tags))

        print ("Ongoing (hour) : \t${:.2f}".format(total_cost_per_hour))
        print ("Ongoing (day) : \t${:.2f}".format(total_cost_per_hour * 24))
        print ("Total accrued cost : \t${:.2f}".format(total_cost))
        print ("Volumes (total) : {}".format(len(volumes)))