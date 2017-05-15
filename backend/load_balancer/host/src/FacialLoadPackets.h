//Defines enumeration of packet states
enum FacialLoadPacketType
{
	Packet = 0x00,
	Authenication = 0x01,
	Health = 0x02,
	Done = 0x03
};

//Defines response codes
enum FacialLoadResponseCode
{
	Initial = 0xF0,
	Accepted = 0xF1,
	Rejected = 0xF2
};
typedef enum FacialLoadPacketType FacialLoadPacketType;
typedef enum FacialLoadResponseCode FacialLoadResponseCode;

typedef struct FacialLoadPacket FacialLoadPacket;
typedef struct FacialLoadAuthentication FacialLoadAuthentication;
typedef struct FacialLoadHealth FacialLoadHealth;
typedef struct FacialLoadDonePacket FacialLoadDonePacket;

//Defines a packet
struct FacialLoadPacket
{
	int size;
	FacialLoadPacketType type;
	FacialLoadResponseCode response;
};

//Authentication struct
struct FacialLoadAuthentication
{
	int dog;
};

//Defines the health of the computer running facialload
struct FacialLoadHealth
{
	int mem_usage; // in percentage
	int cpu_usage; // in percentage
	int tasks_remaining; //internal tasks_remaining

};

//sent when finished
struct FacialLoadDonePacket
{
	unsigned long finished;
};
