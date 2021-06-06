INSTRUCTIONS = """ ██████╗ ███╗   ██╗███████╗████████╗ █████╗ ███████╗██╗  ██╗    ███████╗██████╗ ██╗  ██╗
██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝    ██╔════╝██╔══██╗██║ ██╔╝
██║   ██║██╔██╗ ██║█████╗     ██║   ███████║███████╗█████╔╝     ███████╗██║  ██║█████╔╝
██║   ██║██║╚██╗██║██╔══╝     ██║   ██╔══██║╚════██║██╔═██╗     ╚════██║██║  ██║██╔═██╗
╚██████╔╝██║ ╚████║███████╗   ██║   ██║  ██║███████║██║  ██╗    ███████║██████╔╝██║  ██╗
 ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝╚═════╝ ╚═╝  ╚═╝

Welcome to the onetask Python SDK. With the authorized Client, you can build and register
custom labeling functions for your project to scale your data labeling.

For best practices, please refer to our documentation. Your API calls are stored to a log
file on your local machine.
_________________________________________________________________________________________
   __   __   __        ___  __  ___            ___  __   __             ___    __
  |__) |__) /  \    | |__  /  `  |     | |\ | |__  /  \ |__)  |\/|  /\   |  | /  \ |\ |
  |    |  \ \__/ \__/ |___ \__,  |     | | \| |    \__/ |  \  |  | /~~\  |  | \__/ | \|
_________________________________________________________________________________________

The following labels are defined in your project (see Config Page in your project):
<label-list>
The following attributes are defined in your project (see Config Page in your project):
<attributes-list>
_________________________________________________________________________________________
                     _  _ _ ____ _  _ ____ ___ ____ ____ ___
                     |_/  | |    |_/  [__   |  |__| |__/  |
                     | \_ | |___ | \_ ___]  |  |  | |  \  |
_________________________________________________________________________________________

You can define your functions as in the following example:
>>> def example_lf(record):
...     '''
...     This is an exemplary labeling function!
...     '''
...
...     if record['attributes'][<attribute>] in ['some-value', 'another-value']:
...         return <label>
...     else:
...         return None

To register this function, you must now wrap it into a onetask LabelingFunction. This is
as simple as follows:
>>> lf = onetask.build_lf(
...     example_lf
... )

Now you can register them using your Client (assuming that you named your Client instance
client):
>>> client.register_lf(lf)

This will initialize your labeling function and execute it in a safe environment on our
servers. You can now use this function in the web application. Also, you can check via
the SDK which labeling functions you already registered:
>>> lf_list = client.get_all_lfs() # you can also access by id

If you want to access records using the Client, you can do so by either fetching records
by id or fetching some sample records, e.g.:
>>> record_list = client.get_sample_records() # you can also access by id

Also, you can initially run your labeling function on your local machine for tests:
>>> record_hit_list = lf.execute(record_list)"""