import requests

class BarqUser:
	def __init__(self, email, auth):
		self.email = email

		self.generalHeaders = {
			"host": "api.barq.app",
			"user-agent": "BarqNext/2.2.0+210",
			"authorization": auth
		}

	def testAuth(self):
		requests.post()

	def getEmail(self):
		return self.email

	def graphqlQuery(self, variables, query, extraData={}, operationName=None):
		data = {
			"operationName": operationName,
			"variables": variables,
			"query": query
		}

		data.update(extraData)

		res = requests.post("https://api.barq.app/graphql", headers=self.generalHeaders, json=data)

		if res.status_code == 200:
			return res.json()
		else:
			print("Error making request.", res.text)

			return {}

	def getCurrentEvents(self):
		variables = {
			"limit": 10,
			"offset": 0
		}
		query = "query PopularEvents($limit: Int, $offset: Int) { events(sort: Popular, limit: $limit, offset: $offset) { displayName } }"

		res = self.graphqlQuery(variables, query)

	def getUsersByDistance(self, geoCords, cursor=0, limit=30, requireProfileImage=False, interests=[]):

		query = """query ProfileOverview($cursor: String!, $filters: ProfileSearchFiltersInput!, $isAd: Boolean) {{ profiles: profileSearch(filters: $filters, limit: {limit}, cursor: $cursor, isAd: $isAd) {{ id uuid username displayName age location {{ type distance place {{ id place region country countryCode longitude latitude }} homePlace {{ id place region country countryCode longitude latitude }} }} bio {{ biography relationshipStatus sexualOrientation genders hobbies {{ id interest }} }} profileImage {{ id image {{ id uuid url contentRating }} accessPermission }} socialAccounts {{ id socialNetwork isVerified url displayName value accessPermission }} groups {{ group {{ id uuid displayName isAd contentRating image {{ id uuid url contentRating }} }} }} }} }}"""
		query = query.format(limit=limit)

		variables = {
			"cursor": str(cursor),
			"filters": {
				"location": {
					"latitude": geoCords[0],
					"longitude": geoCords[1],
					"type": "distance"
				},
				"requireProfileImage": requireProfileImage
			},
			"isAd": False
		}

		if len(interests) > 0:
			variables["filters"]["interests"] = interests
		
		return self.graphqlQuery(variables, query)

	def getGroupMembers(self, groupUUID, limit=30, offset=0):
		query = "query GroupMembers($uuid: String!, $offset: Int!, $limit: Int!, $search: GroupMemberSearchInput) {\n  groupMembers(uuid: $uuid, offset: $offset, limit: $limit, search: $search) {\n    pageInfo {\n      ...PageInfo\n      __typename\n    }\n    totalCount\n    edges {\n      node {\n        ...GroupMember\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PageInfo on PageInfo {\n  hasNextPage\n  hasPreviousPage\n  startCursor\n  endCursor\n  __typename\n}\n\nfragment GroupMember on GroupMember {\n  id\n  profile {\n    ...MinimalProfile\n    __typename\n  }\n  roles\n  createdAt\n  __typename\n}\n\nfragment MinimalProfile on Profile {\n  id\n  uuid\n  displayName\n  username\n  relationType\n  roles\n  profileImage {\n    ...MinimalProfileImage\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalProfileImage on ProfileImage {\n  id\n  image {\n    ...MinimalUploadedImage\n    __typename\n  }\n  accessPermission\n  __typename\n}\n\nfragment MinimalUploadedImage on UploadedImage {\n  id\n  uuid\n  url\n  contentRating\n  blurHash\n  __typename\n}"

		variables = {
			"uuid": groupUUID,
			"offset": offset,
			"limit": limit,
			"search": {}
		}
		
		return self.graphqlQuery(variables, query)

	def queryUser(self, username):
		query = "query ProfileSearch($cursor: String! = \"0\", $query: String!, $location: SearchLocationInput) {\n  profiles: profileSearch(filters: {displayName: $query, location: $location}, limit: 30, cursor: $cursor) {\n    ...OverviewProfile\n    __typename\n  }\n  __typename\n}\n\nfragment OverviewProfile on Profile {\n  ...MinimalProfile\n  profileImageAd: profileImage(isAd: true) {\n    ...MinimalProfileImage\n    __typename\n  }\n  location {\n    ...ProfileLocation\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalProfile on Profile {\n  id\n  uuid\n  displayName\n  username\n  relationType\n  roles\n  profileImage {\n    ...MinimalProfileImage\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalProfileImage on ProfileImage {\n  id\n  image {\n    ...MinimalUploadedImage\n    __typename\n  }\n  accessPermission\n  __typename\n}\n\nfragment MinimalUploadedImage on UploadedImage {\n  id\n  uuid\n  url\n  contentRating\n  blurHash\n  __typename\n}\n\nfragment ProfileLocation on ProfileLocation {\n  type\n  distance\n  place {\n    ...Place\n    __typename\n  }\n  homePlace {\n    ...Place\n    __typename\n  }\n  __typename\n}\n\nfragment Place on Place {\n  id\n  place\n  region\n  country\n  countryCode\n  longitude\n  latitude\n  __typename\n}"

		variables = {
			"query": username,
			"location": {
				"latitude": 35.216394,
				"longitude": -113.037602
			}
		}
		
		return self.graphqlQuery(variables, query)

	def queryUserDetails(self, userID):
		# None functional must pass uuid
		return
		query = "query ProfileDetail($uuid: String!) {\n  profile(uuid: $uuid, location: $location) {\n    ...DetailProfile\n    __typename\n  }\n  __typename\n}\n\nfragment DetailProfile on Profile {\n  ...OverviewProfile\n  isAdOptIn\n  isBirthday\n  age\n  shareHash\n  awards {\n    id\n    createdAt\n    award {\n      ...Award\n      __typename\n    }\n    __typename\n  }\n  privacySettings {\n    ...PrivacySettings\n    __typename\n  }\n  images {\n    ...GalleryProfileImage\n    __typename\n  }\n  bio {\n    ...ProfileBioWithInterests\n    __typename\n  }\n  bioAd {\n    ...ProfileBioAd\n    __typename\n  }\n  sonas {\n    ...Sona\n    __typename\n  }\n  kinks {\n    ...ProfileKink\n    __typename\n  }\n  groups {\n    ...ProfileGroup\n    __typename\n  }\n  events {\n    ...ProfileEvent\n    __typename\n  }\n  socialAccounts {\n    ...SocialAccount\n    __typename\n  }\n  __typename\n}\n\nfragment OverviewProfile on Profile {\n  ...MinimalProfile\n  profileImageAd: profileImage(isAd: true) {\n    ...MinimalProfileImage\n    __typename\n  }\n  location {\n    ...ProfileLocation\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalProfile on Profile {\n  id\n  uuid\n  displayName\n  username\n  relationType\n  roles\n  profileImage {\n    ...MinimalProfileImage\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalProfileImage on ProfileImage {\n  id\n  image {\n    ...MinimalUploadedImage\n    __typename\n  }\n  accessPermission\n  __typename\n}\n\nfragment MinimalUploadedImage on UploadedImage {\n  id\n  uuid\n  url\n  contentRating\n  blurHash\n  __typename\n}\n\nfragment ProfileLocation on ProfileLocation {\n  type\n  distance\n  place {\n    ...Place\n    __typename\n  }\n  homePlace {\n    ...Place\n    __typename\n  }\n  __typename\n}\n\nfragment Place on Place {\n  id\n  place\n  region\n  country\n  countryCode\n  longitude\n  latitude\n  __typename\n}\n\nfragment Award on Award {\n  id\n  name\n  title\n  description\n  icon\n  rarity\n  series\n  createdAt\n  __typename\n}\n\nfragment PrivacySettings on PrivacySettings {\n  startChat\n  viewAge\n  viewAd\n  viewKinks\n  viewProfile\n  viewPreciseLocation\n  showLastOnline\n  showOnMap\n  __typename\n}\n\nfragment GalleryProfileImage on ProfileImage {\n  ...MinimalProfileImage\n  likeCount\n  hasLiked\n  isAd\n  __typename\n}\n\nfragment ProfileBioWithInterests on ProfileBio {\n  ...ProfileBio\n  ...ProfileInterests\n  __typename\n}\n\nfragment ProfileBio on ProfileBio {\n  id\n  biography\n  genders\n  languages\n  relationshipStatus\n  sexualOrientation\n  __typename\n}\n\nfragment ProfileInterests on ProfileBio {\n  hobbies {\n    ...Interest\n    __typename\n  }\n  __typename\n}\n\nfragment Interest on Interest {\n  id\n  interest\n  __typename\n}\n\nfragment ProfileBioAd on ProfileBioAd {\n  id\n  biography\n  sexPositions\n  behaviour\n  safeSex\n  canHost\n  __typename\n}\n\nfragment Sona on Sona {\n  id\n  displayName\n  images {\n    id\n    __typename\n  }\n  description\n  hasFursuit\n  species {\n    ...Species\n    __typename\n  }\n  __typename\n}\n\nfragment Species on Species {\n  id\n  displayName\n  popularity\n  __typename\n}\n\nfragment ProfileKink on ProfileKink {\n  id\n  kink {\n    ...Kink\n    __typename\n  }\n  pleasureReceive\n  pleasureGive\n  __typename\n}\n\nfragment Kink on Kink {\n  id\n  displayName\n  categoryName\n  isVerified\n  isSinglePlayer\n  __typename\n}\n\nfragment ProfileGroup on ProfileGroup {\n  group {\n    ...MinimalGroup\n    __typename\n  }\n  threadCount\n  replyCount\n  __typename\n}\n\nfragment MinimalGroup on Group {\n  id\n  uuid\n  displayName\n  isAd\n  contentRating\n  image {\n    ...MinimalUploadedImage\n    __typename\n  }\n  __typename\n}\n\nfragment ProfileEvent on ProfileEvent {\n  event {\n    id\n    uuid\n    displayName\n    isAd\n    contentRating\n    eventBeginAt\n    eventEndAt\n    image {\n      ...MinimalUploadedImage\n      __typename\n    }\n    __typename\n  }\n  isWaitingList\n  __typename\n}\n\nfragment SocialAccount on ProfileSocialAccount {\n  id\n  socialNetwork\n  isVerified\n  url\n  displayName\n  value\n  accessPermission\n  __typename\n}"

		variables = {
			"id": userID,
		}

		return self.graphqlQuery(variables, query)

	def likeProfile(self, userUuid):
		query = "mutation LikeProfile($uuid: String!) {\n  likeProfile(uuid: $uuid)\n  __typename\n}"

		variables = {
			"uuid": userUuid,
		}

		return self.graphqlQuery(variables, query)

	def getChatRequests(self):
		query = "query ChatOverview{chatRooms { id uuid status lastMessage{profile{id}}}}"

		return self.graphqlQuery({}, query)

	def accecptChatRequest(self, roomId):
		query = """mutation AcceptChatRequest($roomId: Int!) {\n  chatRoomRequestAccept(roomId: $roomId) {\n    ...OverviewChat\n    __typename\n  }\n  __typename\n}\n\nfragment OverviewChat on ChatRoom {\n  id\n  uuid\n  type\n  title\n  image {\n    ...MinimalUploadedImage\n    __typename\n  }\n  participantCount\n  lastReadSeqId\n  lastSeqId\n  status\n  isArchived\n  isRemoved\n  lastMessage {\n    ...ChatMessage\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalUploadedImage on UploadedImage {\n  id\n  uuid\n  url\n  contentRating\n  blurHash\n  __typename\n}\n\nfragment ChatMessage on ChatRoomMessage {\n  id\n  seqId\n  createdAt\n  updatedAt\n  deletedAt\n  profile {\n    id\n    __typename\n  }\n  payload {\n    ... on ChatRoomMessagePayloadText {\n      content\n      __typename\n    }\n    ... on ChatRoomMessagePayloadSystem {\n      action\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"""
		variables = {
			"roomId": roomId,
		}

		return self.graphqlQuery(variables, query)
	
	def sendMessage(self, roomId, content):
		query = "mutation SendChatRoomMessage($roomId: Int!, $message: ChatRoomMessageInput!) {\n  chatRoomMessageSend(roomId: $roomId, message: $message) {\n    ...ChatMessage\n    __typename\n  }\n  __typename\n}\n\nfragment ChatMessage on ChatRoomMessage {\n  id\n  seqId\n  createdAt\n  updatedAt\n  deletedAt\n  profile {\n    id\n    __typename\n  }\n  payload {\n    ... on ChatRoomMessagePayloadText {\n      content\n      __typename\n    }\n    ... on ChatRoomMessagePayloadSystem {\n      action\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"

		variables = {
			"roomId": roomId,
			"message": {
      			"content": content
    		}
		}

		return self.graphqlQuery(variables, query)
	
	# use this func to get participants
	def getChatDetails(self, roomId):
		query = "query ChatDetail($roomId:Int!){chatRoom(roomId:$roomId){id uuid participants{profile{id uuid}}}}"

		variables = {
			"roomId": roomId,
		}

		return self.graphqlQuery(variables, query)

	def getSingleUserChatroomInfo(self, uuid):
		query = "query ChatPrivate($profileUuid:String!){chatRoomPrivate(profileUuid:$profileUuid){id uuid status}}"

		variables = {
			"profileUuid": uuid
		}

		return self.graphqlQuery(variables, query)

	def getChatHistory(self, roomId, limit=10):
		"""
		res = self.getSingleUserChatroomInfo(uuid)

		if "data" not in res and "chatRoomPrivate" not in res["data"] and res["data"]["chatRoomPrivate"]["status"]:
			print("Unable to get uuid")
			return res
		"""
		
		variables = {
			"roomId": roomId,
			"limit": limit
		}

		query = "query ChatMessages($roomId:Int!,$cursor:Int,$limit:Int!){chatRoomMessages(roomId:$roomId,cursor:$cursor,limit:$limit){id seqId createdAt profile{id} payload{...on ChatRoomMessagePayloadText{content}}}}"

		return self.graphqlQuery(variables, query)
    
