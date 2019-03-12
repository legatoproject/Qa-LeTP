#include "legato.h"
#include "interfaces.h"

#define PUBLISHER_MAX_CHECK 5

char DeviceIMEI[LE_INFO_IMEI_MAX_BYTES];
mqtt_SessionRef_t MQTTSession;

const char *testAppName = NULL;
bool testResult = true;

char clientId[32];
const uint16_t keepAliveInSeconds = 60;
const bool cleanSession = true;
const char* username = DeviceIMEI;
const uint16_t connectTimeout = 20;
const uint16_t retryInterval = 10;


static void _final_verdict(bool result, const char *testAppName)
{
    if (!result)
        printf("%s: TEST FAILED\n", testAppName);
    exit(((!result) ? EXIT_SUCCESS : EXIT_FAILURE));
}

static void PrintUsage(void)
{
    printf("%s: INFO. Usage Manual:\n", testAppName);
    printf("app runProc %s %s -- publisher <tcp://broker_server_ip:port>\n", testAppName, testAppName);
    printf("app runProc %s %s -- subscriber <tcp://broker_server_ip:port>\n", testAppName, testAppName);
    _final_verdict(false, testAppName);
}

// Check minimum argument number (of expected_nb_arg)
static void Check_AppCtrlNbArg(size_t expected_nb_arg)
{
    size_t nb_arg = le_arg_NumArgs();

    if (!testAppName)
        testAppName = le_arg_GetProgramName();

    if (nb_arg < expected_nb_arg)
    {
        printf("%s: ERROR. Missing arguments.\n", testAppName);
        PrintUsage();
    }
    return;
}

//Call-back function called on lost connection
static void OnConnectionLost
(
    void* context
)
{
    printf("%s: INFO. Connection lost!\n", testAppName);
}

//Call-back function called on arrived message
static void OnMessageArrived
(
    const char* topic,
    const uint8_t* payload,
    size_t payloadLen,
    void* context
)
{
    char payloadStr[payloadLen + 1];
    memcpy(payloadStr, payload, payloadLen);
    payloadStr[payloadLen] = '\0';
    printf("%s: INFO. Received message! topic: \"%s\", payload: \"%s\"\n", testAppName, topic, payloadStr);
    printf("%s: SUBSCRIBER CHECKED OK\n", testAppName);
    _final_verdict(true, testAppName);
}

//Timer handler for periodically publishing data
static void PublishTimerHandler
(
    le_timer_Ref_t timer
)
{
    static int messageData = 0;
    uint8_t payload[64];
    snprintf((char*)payload, sizeof(payload), "{\"value\":%d}", messageData);
    size_t payloadLen = strlen((char*)payload);
    const bool retain = false;
    char publishTopic[64];
    snprintf(publishTopic, sizeof(publishTopic), "%s/messages/json", DeviceIMEI);
    const le_result_t publishResult = mqtt_Publish(MQTTSession, publishTopic, payload, payloadLen, MQTT_QOS0_TRANSMIT_ONCE,        retain);

    printf("%s: INFO. Published Topic %s data %s result %s\n", testAppName, publishTopic, payload,
            LE_RESULT_TXT(publishResult));
    if (publishResult != LE_OK)
    {
        printf ("%s: INFO. LE_OK should be obtained for mqtt_Publish()\n", testAppName);
        testResult = false;
    }
    messageData++;
    if (messageData == PUBLISHER_MAX_CHECK)
    {
        if (testResult)
            printf("%s: PUBLISHER CHECKED OK\n", testAppName);
        _final_verdict(testResult, testAppName);
    }
}

bool checkPublisher()
{
    bool ret = true;
    le_result_t res = LE_OK ;

    const char *mqttBrokerURI = le_arg_GetArg(1);
    printf("%s: INFO. Checking publisher started - Broker URI: %s\n", testAppName, mqttBrokerURI);
    res = le_info_GetImei(DeviceIMEI, NUM_ARRAY_MEMBERS(DeviceIMEI));
    if (res != LE_OK)
    {
        printf("%s: ERROR. LE_OK should be obtained for le_info_GetImei() %d\n", testAppName, res);
        return false;
    }
    else
    {
        printf("%s: INFO. Device IMEI: %s\n", testAppName, DeviceIMEI);
    }

    snprintf(clientId, sizeof(clientId), "%s-pub", DeviceIMEI);
    printf("%s: INFO. Client ID: %s\n", testAppName, clientId);
    res = mqtt_CreateSession(mqttBrokerURI, clientId, &MQTTSession);
    if (res != LE_OK)
    {
        printf("%s: ERROR. LE_OK should be obtained for mqtt_CreateSession() %d\n", testAppName, res);
        return false;
    }
    else
    {
        printf("%s: INFO. Create MQTT session successfully\n", testAppName);
    }

    mqtt_SetConnectOptions(MQTTSession, keepAliveInSeconds, cleanSession, username, NULL, 0, connectTimeout, retryInterval);

    mqtt_AddConnectionLostHandler(MQTTSession, &OnConnectionLost, NULL);
    mqtt_AddMessageArrivedHandler(MQTTSession, &OnMessageArrived, NULL);

    res = mqtt_Connect(MQTTSession);
    if (res != LE_OK)
    {
        printf("%s: ERROR. LE_OK should be obtained for mqtt_Connect() %d\n", testAppName, res);
        ret = false;
    }
    else
    {
        printf("%s: INFO. Connected to server '%s'\n", testAppName, mqttBrokerURI);
        le_timer_Ref_t timer = le_timer_Create("MQTT Publish");
        res = le_timer_SetHandler(timer, &PublishTimerHandler);
        if(res != LE_OK)
        {
            printf("%s: ERROR. LE_OK should be obtained for le_timer_SetHandler() %d\n", testAppName, res);
            ret = false;
        }
        res = le_timer_SetMsInterval(timer, 10000);
        if(res != LE_OK)
        {
            printf("%s: ERROR. LE_OK should be obtained for le_timer_SetMsInterval() %d\n", testAppName, res);
            ret = false;
        }

        res = le_timer_SetRepeat(timer, 0);
        if(res != LE_OK)
        {
            printf("%s: ERROR. LE_OK should be obtained for le_timer_SetRepeat() %d\n", testAppName, res);
            ret = false;
        }

        res = le_timer_Start(timer);
        if(res != LE_OK)
        {
            printf("%s: ERROR. LE_OK should be obtained for le_timer_Start() %d\n", testAppName, res);
            ret = false;
        }

        printf("%s: INFO. Publish timer started\n", testAppName);
    }
    return ret;
}

bool checkSubscriber()
{
    bool ret = true;
    le_result_t res = LE_OK ;
    // server is running on the Linux workstation connected to the target
    const char *mqttBrokerURI = le_arg_GetArg(1);

    printf("%s: INFO. Checking subscriber started - Broker URI: %s\n", testAppName, mqttBrokerURI);
    res = le_info_GetImei(DeviceIMEI, NUM_ARRAY_MEMBERS(DeviceIMEI));
    if (res != LE_OK)
    {
        printf("%s: ERROR. LE_OK should be obtained for le_info_GetImei() %d\n", testAppName, res);
        return false;
    }
    else
    {
        printf("%s: INFO. Device IMEI: %s\n", testAppName, DeviceIMEI);
    }


    snprintf(clientId, sizeof(clientId), "%s-sub", DeviceIMEI);
    res = mqtt_CreateSession(mqttBrokerURI, clientId, &MQTTSession);
    if (res != LE_OK)
    {
        printf("%s: ERROR. LE_OK should be obtained for mqtt_CreateSession() %d\n", testAppName, res);
        return false;
    }
    else
    {
        printf("%s: INFO. Create MQTT session successfully\n", testAppName);
    }

    mqtt_SetConnectOptions(MQTTSession, keepAliveInSeconds, cleanSession, username, NULL, 0, connectTimeout, retryInterval);

    mqtt_AddConnectionLostHandler(MQTTSession, &OnConnectionLost, NULL);
    mqtt_AddMessageArrivedHandler(MQTTSession, &OnMessageArrived, NULL);

    res = mqtt_Connect(MQTTSession);
    if (res != LE_OK)
    {
        printf("%s: ERROR. LE_OK should be obtained for mqtt_Connect() %d\n", testAppName, res);
        ret = false;
    }
    else
    {
        char subscribeTopic[64];

        snprintf(subscribeTopic, sizeof(subscribeTopic), "%s/messages/json", DeviceIMEI);
        res = mqtt_Subscribe(MQTTSession, subscribeTopic, MQTT_QOS0_TRANSMIT_ONCE);
        if (res != LE_OK)
        {
            printf("%s: ERROR. Failed to subscriber to %s\n", testAppName, subscribeTopic);
            ret = false;
        }
        else
        {
            printf("%s: INFO. Subscribed to topic %s\n", testAppName,subscribeTopic);
        }
    }
    printf("%s: SUBSCRIBER STARTED\n", testAppName);
    return ret;
}

COMPONENT_INIT
{
    Check_AppCtrlNbArg(2);
    const char *option = le_arg_GetArg(0);
    if (strcmp(option, "publisher") == 0)
    {
        checkPublisher();
    }
    else if (strcmp(option, "subscriber") == 0)
    {
        checkSubscriber();
    }
    else
    {
        PrintUsage();
    }
}
