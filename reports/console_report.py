

from __future__ import print_function


class ConsoleReporter(object):

    def write(self, instances, volumes):

        instances.sort(key=lambda x: x.cost, reverse=True)
        total_cost = 0
        total_cost_per_hour = 0
        print("Instances")
        for instance in instances:

            total_cost += instance.cost
            total_cost_per_hour += instance.cost_per_hour
 
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
        print ("Ongoing (30 day month) : \t${:.2f}".format(total_cost_per_hour * 24 * 30))
        print ("Total accrued cost : \t${:.2f}".format(total_cost))
        
        print ("Volumes")
        print ("Volumes (total) : {}".format(len(volumes)))
        
        volumes_cost_per_month = 0

        for volume in volumes:
            volumes_cost_per_month += volume.cost
            # print("{} ${:.2f} \t{} \t{} \t{} \t{} \t{}".format(
            #                                 volume.createdAtUtc,
            #                                 volume.cost,
            #                                 volume.identifier,
            #                                 volume.type,
            #                                 volume.aws_region,
            #                                 volume.size,
            #                                 volume.provisioned_iops))
            # print("${:.2f} ${:.2f}".format(
            #     volume.cost_per_gb, 
            #     volume.iops_cost))
        print ("Ongoing (30 day month) : \t${:.2f}".format(volumes_cost_per_month ))
