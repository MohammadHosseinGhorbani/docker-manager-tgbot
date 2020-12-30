from telegram.ext import Updater, Filters, CommandHandler, CallbackQueryHandler
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
import docker as Docker
from time import sleep

container_template = '''**Name**: `{name}`
**Short ID**: `{short_id}`'''

docker = Docker.from_env()

def docker_command(update, context):
    message = update.message
    markup = [[InlineKeyboardButton(i.name, callback_data='cont_' + i.short_id)] for i in docker.containers.list(all=True)]
    message.reply_text('Containers:', reply_markup=InlineKeyboardMarkup(markup), parse_mode='html')

def inline_handler(update, context):
    callback = update.callback_query
    message = callback.message
    data = callback.data

    if data.startswith('cont'):
        container = docker.containers.get(data[5:])
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('Start', callback_data='start_' + container.short_id), InlineKeyboardButton('Stop', callback_data='stop_' + container.short_id), InlineKeyboardButton('Restart', callback_data='restart_' + container.short_id), InlineKeyboardButton('Remove', callback_data='remove_' + container.short_id), InlineKeyboardButton('Logs', callback_data='logs_' + container.short_id)], [InlineKeyboardButton('بازگشت', callback_data='back')]])
        template_args = {'short_id': container.short_id, 'name': container.name}
        message.edit_text(container_template.format(**template_args), reply_markup=markup, parse_mode='markdownv2')

    if data.startswith('start'):
        container = docker.containers.get(data[6:])
        container.start()
        message.edit_text(f'کانتینر {container.name} با موفقیت روشن شد')

    if data.startswith('stop'):
        container = docker.containers.get(data[5:])
        container.stop()
        message.edit_text(f'کانتینر {container.name} با موفقیت خاموش شد')

    if data.startswith('restart'):
        container = docker.containers.get(data[8:])
        container.restart()
        message.edit_text(f'کانتینر {container.name} با موفقیت ری استارت شد')

    if data.startswith('remove'):
        container = docker.containers.get(data[7:])
        try:
            container.remove()
            error = 'کانتینر {container.name} با موفقیت حذف شد'
        except Exception as e:
            error = str(e)
        message.edit_text(error)

    if data.startswith('logs'):
        container = docker.containers.get(data[5:])
        logs = container.logs()
        message.edit_text(message.text_markdown + '\n```Logs``` :```' + logs.decode()[-4000:]+'```', parse_mode='markdownv2', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('بازگشت', callback_data='back')]]))

    if data == 'back':
        markup = [[InlineKeyboardButton(i.name, callback_data='cont_' + i.short_id)] for i in docker.containers.list(all=True)]
        message.edit_text('Containers:', reply_markup=InlineKeyboardMarkup(markup))

def main():
    TOKEN = '<MY_BEAUTIFUL_TOKEN>'
    updater = Updater(TOKEN, use_context=True)
    bot = Bot(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('beta', docker_command))
    dp.add_handler(CallbackQueryHandler(inline_handler))

    updater.start_polling(clean=True)
    print('START')
    updater.idle()


if __name__ == '__main__':
    main()
