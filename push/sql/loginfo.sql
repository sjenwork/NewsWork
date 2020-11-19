SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [ChemiBigData].[dbo].[loginfo](
    [Date] [nvarchar](25) NOT NULL,
	[title] [varchar](128) NULL,
	[content] [text] NULL,
	[updatetime] [datetimeoffset](7) NOT NULL,

) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[loginfo] ADD  DEFAULT (sysdatetimeoffset()) FOR [updatetime]
GO

