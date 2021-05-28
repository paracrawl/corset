import time
import sys
import traceback


from back.tasks import tasks

filepath = sys.argv[1]
filename = sys.argv[2]
collection_id = sys.argv[3]
src_lang_id = sys.argv[4]
trg_lang_id = sys.argv[5]
out_format = sys.argv[6]
sents = sys.argv[7]


task = tasks.generate_corset.apply_async(args=[filepath, filename, collection_id, src_lang_id, trg_lang_id, out_format, sents])
task_id = task.id

print("Task has been launched with ID {}".format(task_id))

task_info = tasks.generate_corset.AsyncResult(task_id)

while task_info.status == "PENDING":
    
    print("Waiting! Status is {}".format(task_info.status))
    time.sleep(1)
    task_info = tasks.generate_corset.AsyncResult(task_id)

try:
    task_data = task_info.get()
    print("Status is {}. The result of the task is: {}".format(task_info.status, task_data))
except Exception as e:
    print("Ops! The task threw an exception! The status is {}".format(task_info.status))
    print("Exception is: {}".format(e))
    #traceback.print_exc()

