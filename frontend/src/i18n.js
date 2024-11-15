import { createI18n } from 'vue-i18n';

const messages = {
  en: {
    mobile: 'You can use this website only by PC and laptop.',
    back_to_bot: ' Back to Raptor bot',
    validator_launcher: 'Validator Launcher',
    validating_link: ' Validating link, please wait...',
    validated_link_error: 'Invalid link or this link has already been used. We have sent you a new link to the bot.',
    sending_transaction: ' Sending transaction, please wait...',
    connecting_wallet: ' Connecting wallet, please wait..',
    redelegate_to_developers: 'Would you like to redelegate another tokens to encourage Raptor developers?',
    thanks: 'Thank you friend!',
    connected_message: 'Connected with address: {address} on {network} network',
    failed_to_connect_keplr: 'Failed to connect Keplr. Please try again. Error: {error}',
    transaction_success: 'Transaction successful! Hash: {hash}',
    redelegate_failed: 'Failed to send redelegate transaction. Please try again. Error: {error}',
    send_redelegate_msg: 'Send Redelegate Authz',
    no_tokens_message: "I don't have tokens {chain}"

  },
  ru: {
    mobile: 'Вы можете использовать этот сайт только на ПК и ноутбуке.',
    back_to_bot: ' Вернуться в Raptor бот',
    validator_launcher: 'Запуск Валидатора',
    validating_link: ' Валидирую ссылку, пожалуйста подождите...',
    validated_link_error: 'Неверная или уже использованная ссылка. Мы отправили новую ссылку в бота.',
    sending_transaction: ' Отправляем транзакцию, пожалуйста подождите...',
    connecting_wallet: ' Подключаем кошелек, пожалуйста подождите..',
    redelegate_to_developers: 'Хотели бы вы ределигировать другие токены для поддержки разработчиков Raptor?',
    thanks: 'Спасибо друг!',
    connected_message: 'Подключен кошелек с адресом {address}, сеть {network}',
    failed_to_connect_keplr: 'Не удалось подключить Keplr. Пожалуйста, попробуйте снова. Ошибка: {error}',
    transaction_success: 'Транзакция прошла успешно! Хеш: {hash}',
    redelegate_failed: 'Не удалось отправить транзакцию перераспределения. Пожалуйста, попробуйте снова. Ошибка: {error}',
    send_redelegate_msg: 'Отправить транзакцию',
    no_tokens_message: "У меня нет токенов {chain}"
  },
};

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages,
});

export default i18n;
